import multiprocessing as mp
from time import sleep


def funcTest(wait, num1, num2):
    # print(f'working with {wait}, {num1}, {num2}')
    sleep(wait)
    # print(f'finished with {wait}, {num1}, {num2}')
    return num1+num2

### A LIST COMPREHENSION WILL GUARANTEE THAT THE RESULTS COME IN THE ORDER OF THE LISTED ARGUMENTS

# if __name__ == '__main__':
#     # pool = mp.Pool(int(mp.cpu_count()/2))
#     pool = mp.Pool(3)
#     paramCombs = [
#         [15, 1, 1], [8, 2, 2], [20, 3, 3], [1, 4, 4], [3, 5, 5]
#     ]
#     res_async = [pool.apply_async(funcTest, args = paramComb) for i,paramComb in enumerate(paramCombs)]
#     results = [r.get() for r in res_async]
#     for res in results:
#         print(res)



### A FOR LOOP WON'T NECESSARY GUARANTEE THAT RESULTS COME IN THE ORDER OF THE FOR LOOP ARGS
def foo_pool(x):
    sleep(2)
    return x*x

def foo_pool_2(x, w):
    sleep(w)
    return x*x

result_list = []
def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)

def apply_async_with_callback():
    pool = mp.Pool()

    # for i in range(10):
    #     pool.apply_async(foo_pool, args = (i, ), callback = log_result)


    waits = [9,5,6,1,1,2,3,8,0,3]
    for i,w in enumerate(waits):
        pool.apply_async(foo_pool_2, args = (i, w), callback = log_result)
    pool.close()
    pool.join()
    print(result_list)

if __name__ == '__main__':
    apply_async_with_callback()