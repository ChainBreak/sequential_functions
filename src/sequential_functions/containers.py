from threading import Thread
import multiprocessing 
from multiprocessing import Process, Queue

class Compose():
    def __init__(self, *functions):
        self.function_list = functions

    def __call__(self, generator):

        for function in self.function_list:
            if isinstance(function, Compose):
                generator = function(generator)
            else:
                generator = self.wrap_function_in_generator(function,generator)

        return generator

    def wrap_function_in_generator(self,function, generator):
        for item in generator:
            yield function(item)

        
class Batch(Compose):
    def __init__(self,*functions, batch_size):
        super().__init__(*functions)

        self.batch_size = batch_size

    def __call__(self,generator):

        batch_generator = self.create_batch_generator(generator)

        batch_generator = super().__call__(batch_generator)

        generator = self.create_debatch_generator(batch_generator)

        return generator

    def create_batch_generator(self,generator):
        batch = []
        for item in generator:
            batch.append(item)
            if len(batch) >= self.batch_size:
                yield batch
                batch = []
        if len(batch) > 0:        
            yield batch

    def create_debatch_generator(self,generator):
        for batch in generator:
            yield from batch



class MultiProcess(Compose):

    class EndToken: pass

    def __init__(self,*functions, num_workers=0):
        super().__init__(*functions)
        self.num_workers = num_workers

    def __call__(self,generator):

        input_queue = Queue(maxsize=1)
        output_queue = Queue(maxsize=1)

        self.start_thread_to_pump_generator_into_queue(generator, input_queue)

        self.start_processes(input_queue, output_queue)


        while True:
            item = output_queue.get()
            print("out queue",item)
            yield item

    
    def start_thread_to_pump_generator_into_queue(self,generator,queue):

        def run():
            for item in generator:
                queue.put(item)

            while True:
                queue.put(self.EndToken())

        thread = Thread(target=run)
        thread.start()

    def start_processes(self, input_queue, output_queue):
        
        process_list = []
        for i in range(self.num_workers):
            p = Process(
                target=self.run_process,
                args=(input_queue, output_queue),
            )
            p.start()
            process_list.append(p)
        return process_list 

    def run_process(self, input_queue, output_queue):
        print("process started")
        while True:
            item = input_queue.get()
            if isinstance(item, MultiProcess.EndToken):
                break
            output_queue.put(item)
