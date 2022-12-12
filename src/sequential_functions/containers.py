


class Compose():
    def __init__(self, *functions):
        self.function_list = functions

    def __call__(self, generator):

        for function in self.function_list:
            
            if type(function) is type(self):
                generator = function(generator)
            else:
                generator = self.wrap_function_in_generator(function,generator)

        return generator

    def wrap_function_in_generator(self,function, generator):
        for item in generator:
            yield function(item)


class MultiProcessSequence():
    def __init__(self,*callables):
        self.function_list = callables

    def __call__(self,g):
        with Pool(10) as p:
            yield from p.imap(self.forward, g)

    def forward(self,x):
        for f in self.function_list:
            x = f(x)
        return x
        
class Batch():
    def __init__(self,*callables):
        self.function_list = callables
        self.batch_size = 3

    def __call__(self,g):
        batch_g = self.create_batch_generator(g)

        for f in self.function_list:
            batch_g = self.wrap_function_in_generator(f,batch_g)

        g = self.create_debatch_generator(batch_g)
        return g

    def create_batch_generator(self,g):
        batch = []
        for item in g:
            batch.append(item)
            if len(batch) >= self.batch_size:
                yield batch
                batch = []
        yield batch

    def create_debatch_generator(self,g):
        for batch in g:
            yield from batch

    
    def wrap_function_in_generator(self,f, g):
        for x in g:
            yield f(x)

special_callable_types = [type(Compose), type(MultiProcessSequence), type(Batch)]