from threading import Thread
import multiprocessing 
from multiprocessing import Process, Queue
import queue 

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

        self.queue_timeout=0.3

    def __call__(self,generator):

        input_queue = Queue(maxsize=1)
        output_queue = Queue(maxsize=1)

        process_list = self.start_processes(input_queue, output_queue)

        self.start_thread_to_pump_generator_into_queue(generator, input_queue, process_list)

        yield from self.yield_items_from_output_queue_until_complete(output_queue, process_list)

        input_queue.close()
        output_queue.close()
        
    def start_thread_to_pump_generator_into_queue(self, generator, input_queue,process_list ):

        def run():
            for item in generator:
                input_queue.put(item)

            while self.any_process_is_alive(process_list):
                try:
                    input_queue.put(self.EndToken(),timeout=self.queue_timeout)
                except queue.Full:
                    pass
            
        thread = Thread(target=run)
        thread.start()

    def start_processes(self, input_queue, output_queue):
        
        process_list = []
        for i in range(self.num_workers):
            p = Process(
                name=f"MultiProcess_{i}",
                target=self.run_process,
                args=(input_queue, output_queue),
            )
            p.start()
            process_list.append(p)
        return process_list 

    def run_process(self, input_queue, output_queue):
        
        def generator():
            while True:
                item = input_queue.get()
                if isinstance(item, MultiProcess.EndToken):
                    return
                else:
                    yield item

        output_generator = super().__call__( generator() )

        for item in output_generator:
            output_queue.put(item)

    def yield_items_from_output_queue_until_complete(self,output_queue,process_list):
        while True:
            try:
                yield output_queue.get(timeout=self.queue_timeout)

            except queue.Empty:
                if not self.any_process_is_alive(process_list):
                    
                    return

    def any_process_is_alive(self, process_list):
        for process in process_list:
            if process.is_alive():
                return True
        return False
