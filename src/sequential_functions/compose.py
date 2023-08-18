from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import collections
import types
import itertools
import signal
from multiprocessing import  Queue
import queue
from threading import Thread

class Compose():
    # Class used to mark when the last item his entered the queue
    class EndToken: pass

    def __init__(self, *functions, num_processes=0, num_threads=0):
        self.function_list = functions
        self.num_processes = num_processes
        self.num_threads = num_threads
        self.queue_timeout=2.0

    def __call__(self, input_generator):

        if self.num_processes > 0:
            with ProcessPoolExecutor(max_workers=self.num_processes, initializer=self.ignore_keyboard_interrupt_in_process_worker) as process_pool:
                yield from self.run_generator_through_pool_of_workers(input_generator, process_pool, self.num_processes )

        elif self.num_threads > 0:
            with ThreadPoolExecutor(max_workers=self.num_threads) as thread_pool:
                yield from self.run_generator_through_pool_of_workers(input_generator, thread_pool, self.num_threads )

        else:
            yield from self.build_generator_chain(input_generator)


    def ignore_keyboard_interrupt_in_process_worker(self):
        # Make workers ingnore keyboard interrupts to prevent zombie processes.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    def run_generator_through_pool_of_workers(self, input_generator, pool, num_workers):

        # Use queues to allows workers to pull items from the generator before them 
        input_queue = Queue(maxsize=1)
        output_queue = Queue(maxsize=1)


        # Start all the workers and give them the input and output queues
        future_list = []
        for i in range(num_workers):
            print(f"submit worker {i}")
            future = pool.submit(self.worker_function, input_queue, output_queue) 
            future_list.append(future)

        self.pump_generator_into_queue_using_background_thread(input_generator, input_queue)

        
        yield from self.yield_items_from_output_queue_until_all_workers_have_stopped(output_queue, future_list)
        print("Finished yield results")
      
        input_queue.close()
        output_queue.close()

    def pump_generator_into_queue_using_background_thread(self, input_generator, input_queue ):
        def run():
            # Pull items from the generator and put then in the input queue
            for item in input_generator:
                print("into queue",item)
                input_queue.put(item)

            # All done, send an end token to the workers
            input_queue.put(self.EndToken())
 
            return

        thread = Thread(target=run)
        thread.start()

    def worker_function(self,input_queue, output_queue):
        print("worker function called")
        input_generator = self.wrap_queue_as_generator(input_queue)
        
        output_generator = self.build_generator_chain( input_generator )
        
        for item in output_generator:
            output_queue.put(item)

    def wrap_queue_as_generator(self,input_queue):
        while True:
            print("worker getting item from queue")
            item = input_queue.get()
            print("item")
            if isinstance(item, Compose.EndToken):
                # Resend the end token to tell other processes
                input_queue.put(item)

                # Return ends the generator
                return
            else:
                yield item

    def yield_items_from_output_queue_until_all_workers_have_stopped(self,output_queue, future_list):
        while True:
            try:
                yield output_queue.get(timeout=self.queue_timeout)
            except queue.Empty:
                if not any((future.running() for future in future_list)):
                    return

    def build_generator_chain(self, generator):

        for function in self.function_list:
            if isinstance(function, Compose):
                generator = function(generator)
            else:
                generator = self.wrap_function_in_generator(function,generator)

        return generator

    def wrap_function_in_generator(self, function, generator):

        for item in generator:

            result_item = function(item)

            # Functions can return a signle item or yield items as a generator
            if isinstance(result_item, types.GeneratorType):
                yield from result_item
            else:
                yield result_item
   
      
