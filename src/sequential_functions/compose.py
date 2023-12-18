from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import types
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

        # Use a manager to all queue to be passed to background processes
        manager = multiprocessing.Manager()

        # Use queues to allows workers to pull items from the generator before them 
        input_queue = manager.Queue(maxsize=2)
        output_queue = manager.Queue(maxsize=2)
        running_flag = manager.Event()
        running_flag.set()

        input_queue = QueueTimeoutRetryWrapper(input_queue, running_flag)
        retry_output_queue = QueueTimeoutRetryWrapper(output_queue, running_flag)

        try: 
            # Start all the workers and give them the input and output queues
            # Workers read from the input queue and write to the output queue
            worker_list = []
            for i in range(num_workers):
                worker = pool.submit(self.worker_function, input_queue, retry_output_queue) 
                worker_list.append(worker)

            # Read items from generator and put them in queue
            self.pump_generator_into_queue_using_background_thread(input_generator, input_queue)

            # Yield items from the output queue as a generator
            yield from self.yield_items_from_output_queue_until_all_workers_have_stopped(output_queue, worker_list)
            
            # Raise any exceptions that were found in the workers.
            self.raise_any_worker_exception(worker_list)

        finally:
            running_flag.clear()
   
    def pump_generator_into_queue_using_background_thread(self, input_generator, input_queue):
        def run():
            
            # Pull items from the generator and put then im the input queue
            for item in input_generator:
                input_queue.put(item, timeout=self.queue_timeout)

            # All done, send an end token to the workers
            input_queue.put(self.EndToken(), timeout=self.queue_timeout)
 
        thread = Thread(target=run)
        thread.start()

    def worker_function(self,input_queue, output_queue):
     
        input_generator = self.wrap_queue_as_generator(input_queue)
        
        output_generator = self.build_generator_chain( input_generator )
        
        for item in output_generator:
            output_queue.put(item, timeout=self.queue_timeout)

 
    def wrap_queue_as_generator(self,queue):
        while True:
            
            item = queue.get( timeout=self.queue_timeout)
            
            if isinstance(item, Compose.EndToken):
                # Resend the end token to tell other processes
                queue.put(item, timeout=self.queue_timeout)

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

            # Functions can return None, a signle item or a generator that yields items
            if result_item is None:
                # Skip this item and continue with the next one
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

class QueueTimeoutRetryWrapper():
    def __init__(self, queue, running_flag):
        self.queue = queue
        self.running_flag = running_flag

    def put(self,*args,**kwargs):
        while self.running_flag.is_set():
            try:
                return self.queue.put(*args,**kwargs)
            except queue.Full:
                pass
 
    def get(self,*args,**kwargs):
        while self.running_flag.is_set():
            try:
                return self.queue.get(*args,**kwargs)
            except queue.Empty:        
                pass
        
        
                

    