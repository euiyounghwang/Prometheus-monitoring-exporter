import time 
import logging
from threading import Thread

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
 

def test():
    while True:
        logging.info('loading')
        time.sleep(1)


if __name__ == '__main__':
    test()
    try:
        T = []
        # th1 = Thread(target=test)
        # th1.daemon = True
        # th1.start()
        # T.append(th1)
        for host in ['localhost', 'localhost1']:
            th1 = Thread(target=test, args=())
            th1.daemon = True
            th1.start()
            T.append(th1)
        
        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)
        

    except (KeyboardInterrupt, SystemExit):
        logging.info("#Interrupted..")

    finally:
        logging.info("#Interrupted..#2")
    