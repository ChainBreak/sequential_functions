import queue

class QueueGeneratorWrapper():
    """Wrapper around multiprocessing queue that enables it to be used as a 
    generator plus provides methods for retrying.
    Importantly, all loops are stopped if the running_condition evaluates to false. This prevents stuck processes.
    """

    # Class used to mark when the last item his entered the queue
    class EndToken: pass

    
    def __init__(self, queue, timeout, running_condition):
        self.queue = queue
        self.running_condition = running_condition
        self.timeout = timeout

    def enqueue_from_generator(self, generator):

        # Keep pulling items from the generator and putting them in the queue
        for item in generator:

            self.put_retry_if_full(item)

            # Stop pull items if the running_condition is false
            if not self.running_condition():
                break

    def dequeue_as_generator(self):
        while self.running_condition():
            
            item = self.get_retry_if_empty()
            
            if isinstance(item, self.EndToken):
                # Resend the end token to tell other processes
                self.put_retry_if_full(item)

                # Return ends the generator
                return
            else:
                yield item
    
    def put_end_token(self):
        self.put_retry_if_full(self.EndToken())
        
    def put_retry_if_full(self,item):
        # Just keep trying while the running flag is set
        while self.running_condition():
            try:
                return self.put(item, timeout=self.timeout)
            except queue.Full:
                pass
     
    def get_retry_if_empty(self):
        # Just keep trying while the running flag is set
        while self.running_condition():
            try:
                return self.get(timeout=self.timeout)
            except queue.Empty:        
                pass

    def put(self,*args,**kwargs):
        return self.queue.put(*args,**kwargs)

    def get(self,*args,**kwargs):
        return self.queue.get(*args,**kwargs)
        
        
                

    