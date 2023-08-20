from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import types
import signal
import multiprocessing
import queue
from threading import Thread
from.callable import Callable
class Compose(Callable):
    # Class used to mark when the last item his entered the queue
    class EndToken: pass

    def __init__(self, *functions, num_processes=0, num_threads=0):
        self.function_list = functions
        self.num_processes = num_processes
        self.num_threads = num_threads
        self.queue_timeout=0.1

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

        # Generators can't be shared to multiple processes so instead we use queue's. 
        # generator -> queue -> [p1,p2,..,pn] -> queue -> generator

        # Use a manager to all queue to be passed to background processes
        manager = multiprocessing.Manager()

        # Use queues to allows workers to pull items from the generator before them 
        input_queue = manager.Queue(maxsize=1)
        output_queue = manager.Queue(maxsize=1)

        # Read items from generator in put them in queue
        self.pump_generator_into_queue_using_background_thread(input_generator, input_queue)

        # Start all the workers and give them the input and output queues
        # Workers read from the input queue and write to the output queue
        worker_list = []
        for i in range(num_workers):
            worker = pool.submit(self.worker_function, input_queue, output_queue) 
            worker_list.append(worker)

        # Yield items from the output queue as a generator
        yield from self.yield_items_from_output_queue_until_all_workers_have_stopped(output_queue, worker_list)
        
        # Empty the input_queue to allow the processes to stop properly.
        # Processes hang when a queue is not empty
        self.discard_all_items_from_queue(input_queue)
        
        # Raise any exceptions that were found in the workers.
        self.raise_any_worker_exception(worker_list)
        
    def pump_generator_into_queue_using_background_thread(self, input_generator, input_queue ):
        def run():
            # Pull items from the generator and put then in the input queue
            for item in input_generator:
                
                input_queue.put(item)

            # All done, send an end token to the workers
            input_queue.put(self.EndToken())
 
        thread = Thread(target=run)
        thread.start()

    def worker_function(self,input_queue, output_queue):
        
        input_generator = self.wrap_queue_as_generator(input_queue)
        
        output_generator = self.build_generator_chain( input_generator )
        
        for item in output_generator:
            output_queue.put(item)

    def wrap_queue_as_generator(self,input_queue):
        while True:
            
            item = input_queue.get()
            
            if isinstance(item, Compose.EndToken):
                # Resend the end token to tell other processes
                input_queue.put(item)

                # Return ends the generator
                return
            else:
                yield item

    def yield_items_from_output_queue_until_all_workers_have_stopped(self,output_queue, worker_list):
        
        while True:
            try:
                yield output_queue.get(timeout=self.queue_timeout)

            except queue.Empty:
                if not any((worker.running() for worker in worker_list)):
                    return

    def build_generator_chain(self, generator):

        for function in self.function_list:
            if isinstance(function, Callable):
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
   
    def discard_all_items_from_queue(self,queue_to_clean):
        while True:
            try:
                item = queue_to_clean.get(timeout=self.queue_timeout)
            except queue.Empty:
                return
            
    def raise_any_worker_exception(self, worker_list):
        # Raise any exceptions found in workers
        for worker in worker_list:
            exception = worker.exception()
            if exception is not None:
                raise exception
