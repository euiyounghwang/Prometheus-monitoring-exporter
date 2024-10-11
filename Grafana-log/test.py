import time
import os

path = os.path.dirname(os.path.abspath(__file__))


def get_info_error(line, buffer):
    ''' return all wrap log'''
    if 'INFO' in line or 'ERROR' in line:
        if len(buffer) > 0:
            yield ",".join(buffer)
            buffer = []
        buffer.append(line)
    else:
        buffer.append(line)
        

def get_error(line, buffer):
    ''' return only ERROR wrap log'''
    print(line)
    if 'ERROR' in line:
        if len(buffer) > 0:
            yield ",".join(buffer)
            buffer = []
        buffer.append(line)
    else:
        if 'INFO' not in line:
            buffer.append(line)
    print(buffer)
    

def follow(thefile):
    '''generator function that yields new lines in a file
    '''
    # seek the end of the file
    # thefile.seek(0, os.SEEK_END)
    
    buffer = []
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()
        # print(line)
        # sleep if file hasn't been updated
        if not line:
            ''' add new logic'''
            ''' ------------'''
            if len(buffer) > 0:
                yield "".join(buffer)
                buffer = []
            ''' ------------'''
            time.sleep(0.1)
            continue

        # print(line)
        # get_error(line, buffer)
        ''' return only ERROR wrap log'''
        ''' get_error(line, buffer) '''
        """
        if 'ERROR' in line:
            if len(buffer) > 0:
                yield ",".join(buffer)
                buffer = []
            buffer.append(line)
        else:
            if 'INFO' not in line:
                buffer.append(line)
        """

        ''' return all wrap log'''
        ''' get_info_error'''
        if 'INFO' in line or 'ERROR' in line:
            if len(buffer) > 0:
                yield "".join(buffer)
                buffer = []
            buffer.append(line)
        else:
            buffer.append(line)

        # yield line

if __name__ == '__main__':
    ''' Readline with INFO/ERROR with Seek Offset'''
    logfile = open("{}/test.log".format(path),"r")
    loglines = follow(logfile)
    # iterate over the generator
    for idx, line in enumerate(loglines):
        print(line)