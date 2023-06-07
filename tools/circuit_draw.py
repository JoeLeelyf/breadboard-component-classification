import cv2
import os
import schemdraw
import schemdraw.elements as elm
import queue
import random
from collections import deque

'''
    draw_circuit()
    input: circuits_info
        -- form: [(component_name, index_1, index_2)]
            e.g. [('SourceV', 0, 2), ('Resistor', 0, 1), ('Capacitor', 1, 2), ('SourceI', 1, 2)]
    output: path of the image
'''
def draw_circuit(circuits_info, save_dir, save_name):
    d = schemdraw.Drawing()
    # get circuits info
    # circuits = circuits_info
    circuits =  [('Resistor', 0, 1), ('Resistor', 0, 2), ('Resistor', 0, 3), ('Resistor', 1, 3), ('Resistor', 2, 4), ('Resistor', 1, 4)]
    elements = {'Resistor': elm.Resistor, 'Capacitor': elm.Capacitor, 'Diode':elm.Diode, 'Ground': elm.Ground, 'SourceV': elm.SourceV, 'SourceI': elm.SourceI}
    elements_diection_oppsite = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
    labels = {'Resistor': 'R', 'Capacitor': 'C', 'Ground': '', 'SourceV': 'V', 'SourceI': 'I', 'Diode': 'D'}
    dotslen = max([max(circuit[1], circuit[2]) for circuit in circuits]) + 1
    circuit_queue = [queue.Queue() for i in range(dotslen)]
    elements_diection = [['up', 'down', 'left', 'right'] for i in range(dotslen)]
    end_dots = [-1 for i in range(dotslen)]
    temp_dots = deque()
    firstFlag = True

    for circuit in circuits:
        circuit_queue[circuit[1]].put(circuit)
        
    
    while not all([circuit.empty() for circuit in circuit_queue]):
        for i in range(len(circuit_queue)):
            if not circuit_queue[i].empty():
                circuit = circuit_queue[i].get()
                break
    
        while True:
            if firstFlag and circuit[1] == 0 and circuit_queue[circuit[1]].qsize() > 0:
                firstsize = circuit_queue[circuit[1]].qsize()
                if firstsize > 1:
                    d += elm.Dot()
                while firstsize > 0:
                    d.push()
                    temp_dots.append(circuit[1])
                    firstsize -= 1
                firstFlag = False
            
            direction = random.choice(elements_diection[circuit[1]])
            elements_diection[circuit[1]].remove(direction)
            if not circuit_queue[circuit[2]].empty():
                elements_diection[circuit[2]].remove(elements_diection_oppsite[direction])
            d += (t:= elements[circuit[0]](direction).label(labels[circuit[0]]))
            if circuit_queue[circuit[2]].qsize() > 1:
                d += elm.Dot()
            size = circuit_queue[circuit[2]].qsize()
            while size > 1:
                d.push()
                temp_dots.append(circuit[2])
                size -= 1
            
            if end_dots[circuit[1]] == -1:
                end_dots[circuit[1]] = t.start
            if end_dots[circuit[2]] == -1:
                end_dots[circuit[2]] = t.end   
            
            if circuit_queue[circuit[2]].empty():
                if end_dots[circuit[2]] != t.end:
                    d += elm.Line().endpoints(end_dots[circuit[2]], t.end)
                # end_dots[circuit[2]] = t.end
                if temp_dots:
                    if circuit[1] == 0 and circuit_queue[circuit[1]].qsize() > 0:
                        circuit = circuit_queue[temp_dots.pop()].get()
                        d.pop()
                        continue
                    elif circuit[1] != 0:
                        circuit = circuit_queue[temp_dots.pop()].get()
                        d.pop()
                else:
                    break
            else:
                # end_dots[circuit[2]] = t.end
                circuit = circuit_queue[circuit[2]].get()   

    save_path = os.path.join(save_dir, save_name)
    d.draw(show=False)
    d.save(save_path)
    return save_path
