from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import types
import multiprocessing
import queue
from threading import Thread
from .callable import Callable
from .queue_generator_wrapper import QueueGeneratorWrapper

class Compose(Callable):
    
    def __init__(self, *functions, num_processes=0, num_threads=0):
        self.function_list = functions
        self.num_processes = num_processes
        self.num_threads = num_threads
        self.queue_timeout=0.1
        self.queue_maxsize = 2

    def __call__(self, input_generator):
        # Main entry point

        if self.num_processes > 0:
            
            with ProcessPoolExecutor(max_workers=self.num_processes) as process_pool:
                yield from self.run_generator_through_pool_of_workers(input_generator, process_pool, self.num_processes )

        elif self.num_threads > 0:
            
            with ThreadPoolExecutor(max_workers=self.num_threads) as thread_pool:
                yield from self.run_generator_through_pool_of_workers(input_generator, thread_pool, self.num_threads )

        else:
            yield from self.build_generator_chain(input_generator)
    
    def run_generator_through_pool_of_workers(self, input_generator, pool, num_workers):

        # Generators can't be shared to multiple processes so instead we use queue's. 
        # generator -> queue -> [p1,p2,..,pn] -> queue -> generator

        # Use a manager to create all queue to be passed to background processes
        manager = multiprocessing.Manager()

        # Use queues to allows workers to pull items from the generator before them 
        input_queue = manager.Queue(maxsize=self.queue_maxsize)
        output_queue = manager.Queue(maxsize=self.queue_maxsize)

        # Use an event to indiciate if the we're still running.
        # Used to exit loops e.g. while running_flag.is_set(): # do stuff
        running_flag = manager.Event()
        running_flag.set()

        input_queue = QueueGeneratorWrapper(input_queue, self.queue_timeout, running_flag.is_set)
        output_queue = QueueGeneratorWrapper(output_queue, self.queue_timeout, running_flag.is_set)

        try: 
            # Start all the workers and give them the input and output queues
            # Workers read from the input queue and write to the output queue
            worker_list = []
            for i in range(num_workers):
                worker = pool.submit(self.worker_function, input_queue, output_queue) 
                worker_list.append(worker)

            # Read items from generator and put them in queue
            self.pump_generator_into_queue_using_background_thread(input_generator, input_queue)

            # Yield items from the output queue as a generator
            yield from self.yield_items_from_output_queue_until_all_workers_have_stopped(output_queue, worker_list, running_flag)
            
            # Raise any exceptions that were found in the workers.
            self.raise_any_worker_exception(worker_list)

        finally:
            running_flag.clear()
   
    def pump_generator_into_queue_using_background_thread(self, generator, queue):

        def run():
            # Pull items from the generator and put them in the queue
            queue.enqueue_from_generator(generator)

            # All done, send an end token to the workers
            queue.put_end_token()
 
        thread = Thread(target=run)
        thread.start()

    def worker_function(self,input_queue, output_queue):
        
        # Convert queue into generator
        input_generator = input_queue.dequeue_as_generator()
        
        # Do work
        output_generator = self.build_generator_chain( input_generator )
        
        # Convert generator into queue
        output_queue.enqueue_from_generator(output_generator)

    def yield_items_from_output_queue_until_all_workers_have_stopped(self, output_queue, worker_list, running_flag):
        
        while running_flag.is_set():
            try:
                yield output_queue.get(timeout=self.queue_timeout) #QUEUE

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

            # Functions can return None, a signle item or a generator that yields items
            if result_item is None:
                # Skip this item and copump_generator_into_queuentinue with the next one
                continue
            elif isinstance(result_item, types.GeneratorType):
                yield from result_item
            else:
                yield result_item
               
    def raise_any_worker_exception(self, worker_list):
        # Raise any exceptions found in workers
        for worker in worker_list:
            exception = worker.exception()
            if exception is not None:
                raise exception
