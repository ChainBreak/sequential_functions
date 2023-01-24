from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import collections
import types
import itertools

class Compose():
    def __init__(self, *functions, num_processes=0, num_threads=0):
        self.function_list = functions
        self.num_processes = num_processes
        self.num_threads = num_threads

    def __call__(self, input_generator):

        if self.num_processes > 0:
            output_generator = self.build_generator_chain_with_multi_processing(input_generator)
        elif self.num_threads > 0:
            output_generator = self.build_generator_chain_with_multi_threading(input_generator)
        else:
            output_generator = self.build_generator_chain(input_generator)
        return output_generator

    def build_generator_chain_with_multi_processing(self,generator):

        with ProcessPoolExecutor(max_workers=self.num_processes) as pool:
            for collated_items in self.map_with_pool_executor(pool, self.worker_function, generator):

                for item in collated_items:
                    yield item
    
    def build_generator_chain_with_multi_threading(self,generator):

        with ThreadPoolExecutor(max_workers=self.num_threads) as pool:
            for collated_items in self.map_with_pool_executor(pool, self.worker_function, generator):

                for item in collated_items:
                    yield item

    def map_with_pool_executor(self, pool_excecutor, function,  generator):
        
        # generator that submits work to the pool excecutor and yields futures
        future_generator = ( pool_excecutor.submit(function, item) for item in generator )

        # Submit enough work to fill all workers
        pending_futures = itertools.islice(future_generator, pool_excecutor._max_workers)

        # Queue up the pending work
        pending_futures = collections.deque(pending_futures)

        while pending_futures:
            future = pending_futures.popleft()

            yield future.result()

            # Submit more work and add the future to the queue
            # Using for as an easy way to pull the next item
            for future in future_generator:
                pending_futures.append(future)
                break


    def worker_function(self,item):

        output_generator = self.build_generator_chain( [item] )

        # Use list to collate items incase there are more outputs than inputs
        return list(output_generator)

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

            # Functions can return item or  yield items as a generator
            if isinstance(result_item, types.GeneratorType):
                yield from result_item
            else:
                yield result_item
   
      
