import random
import simpy

MACHINE = 3  # number of machines
JOB = 5  # number of jobs
OPR_MIN = 2  # minimum number of operations
OPR_MAX = 5  # maximum number of operations

def job(env, j):
    n_o = random.randint(OPR_MIN, OPR_MAX)  # number of operations of job j
    p_r = random.choices(range(MACHINE), k=n_o)  # processing route
    p_t = [random.randint(2,7) for o in range(n_o)]  # processing times
    for o in range(n_o):
        m = env.machines[p_r[o]]  # which machine to use
        with m.request() as req:
            yield req
            s_t = round(env.now)  # start time
            yield env.timeout(p_t[o])
            c_t = round(env.now)  # completion time
            print('o_{}_{} on m_{}: {}-{}'.format(j, o, p_r[o], s_t, c_t))

def main():
    env = simpy.Environment()
    env.machines = [simpy.Resource(env) for m in range(MACHINE)]
    for j in range(JOB):
        env.process(job(env, j))
    env.run()

if __name__ == "__main__":
    main()
