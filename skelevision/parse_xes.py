from xmlr import xmlparse, xmliter
import xml.etree.ElementTree as etree
from pm4py.objects.log.importer.xes import factory as xes_import_factory
import os, timeit


UPLOAD_FOLDER = "./uploads"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, UPLOAD_FOLDER)
FILENAME_XES = "BPI_Challenge_2017.xes"
FILENAME_TXT = "L1.txt"
filename = DATA + "/" + FILENAME_XES


def parse_xes():
    with open(filename, 'r+') as dataset:
        data = etree.parse(dataset)
        root = data.getroot()

        tracelog = dict()
        for item in root.findall('./trace'):
            single_trace = []
            for events in item:
                for event in events:
                    if event.tag == "string":
                        #print(len(event.attrib), " ", type(event.attrib), " ", event.attrib)
                        if event.attrib["key"] == "concept:name":
                            # print(event.attrib["value"])
                            single_trace.append(event.attrib["value"])

            if tuple(single_trace) not in tracelog:
                tracelog[tuple(single_trace)] = 0

            tracelog[tuple(single_trace)] += 1

    return tracelog

def parse_xes_pm4py():
    tracelog = dict()
    # log = xes_importer.apply(dataset)
    log = xes_import_factory.apply(filename)
    for case in log:
        a = tuple([event["concept:name"] for event in case])

        if a not in tracelog:
            tracelog[a] = 0
        tracelog[a] += 1

    return tracelog



if __name__ == "__main__":
    start1 = timeit.default_timer()
    tracelog1 = parse_xes()
    # print(tracelog)
    print("length: ", len(tracelog1))
    stop1 = timeit.default_timer()
    print('Time: ', stop1 - start1)

    start2 = timeit.default_timer()
    tracelog2 = parse_xes_pm4py()
    print(len(tracelog2))
    stop2 = timeit.default_timer()
    print('Time: ', stop2 - start2)


    for trace in tracelog1:
        assert trace in tracelog2

    for trace in tracelog2:
        assert trace in tracelog1
