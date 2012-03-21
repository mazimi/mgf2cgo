#!/usr/bin/python -tt


import argparse
import re


def main(mgf, seq, static):

   typeVertex = False
   typeSphere = False
   flagColor = False
   flagElement = False
   flagCoords = False
   frame = 0
   currRGB = [-1.0] * 3
   lastRGB = [-1.0] * 3
   XYZ = [0.0] * 3
   element = ''
   listElements = []
   obj = ''
   strObj = ''

   fin = open(mgf, 'rU')
   fout = open(seq, 'w')

   seqHeader = 'from pymol.cgo import *\nfrom pymol import cmd\n#Script generated using MGF2CGO\n'
   fout.write(seqHeader)

   for line in fin:
      #Line beginning with 'step' followed by a number indicates frame
      match = re.search(r'step(\d+)', line)
      if match:
         if frame > 0:
            fout.write('\t]\n')
            for obj in listElements:
               strObj += obj + ' + '
            fout.write('obj = ' + strObj[:-3] + '\n')
            fout.write('cmd.load_cgo(obj,\'segment\',\t' + str(frame) + ')\n')
            strObj = ''
            listElements = []

         frame = int(match.group(1))
         flagCoords = False
         typeVertex = False
         typeSphere = False
         continue


      #Set type to VERTEX
      match = re.search(r'disjoint line', line)
      if match:
         if element != static or frame == 1:
            if typeVertex:
               fout.write('\tEND\n\t]\n')
            elif typeSphere:
               fout.write('\t]\n')
         typeVertex = True
         typeSphere = False
         flagElement = True
         continue

      #Set type to SPHERE
      match = re.search(r'sphere', line)
      if match:
         if element != static or frame == 1:
            if typeVertex:
               fout.write('\tEND\n\t]\n')
            elif typeSphere:
               fout.write('\t]\n')
         typeVertex = False
         typeSphere = True
         flagElement = True
         continue

      #Determine element name
      if flagElement:
         match = re.search(r'^\s*([\w|\-]+)\s*$', line)
         if match:
            element = match.group(1)
            #Add underscore to element names that begin with a number
            match = re.search(r'\d', element[0])
            if match:
               element = '_' + element
            #Replace dashes w/ underscores
            element = element.replace('-','_')
            listElements.append(element)
            flagElement = False
            flagColor = False

            if element == static and frame > 1:
               continue

            fout.write(element + ' = [\n')
            if typeVertex:
               fout.write('\tLINEWIDTH, 1.0, BEGIN, LINES,\n')
         continue

      #Check to see if color used (TODO: add option for non-color)
      match = re.search(r'color', line)
      if match:
         flagColor = True
         continue

      #Single number on entire line represents number of elements
      #except for total number of steps at beginning of file (ignored)
      match = re.search(r'^\s*(\d+)\s*$', line)
      if match:
         numElements = int(match.group(1))
         flagCoords = True
         currRGB = [-1.0, -1.0, -1.0]
         continue

      #If expecting coordinates and a first step has been encountered
      #(to avoid looking for coords after initial file comments)
      if flagCoords and frame > 0:
         if element == static and frame > 1:
            continue
         if typeSphere:
            match = re.search(r'(-?\d\d?\.\d\d)\s+(-?\d\d?\.\d\d)\s+(-?\d\d?\.\d\d)\s+(\d\d?\.\d\d)\s+(\d\.\d\d)\s+(\d\.\d\d)\s+(\d\.\d\d)', line)
            if match:
               XYZ[0] = float(match.group(1))
               XYZ[1] = float(match.group(2))
               XYZ[2] = float(match.group(3))
               rad = float(match.group(4))
               lastRGB[:] = currRGB[:]
               currRGB[0] = float(match.group(5))
               currRGB[1] = float(match.group(6))
               currRGB[2] = float(match.group(7))

               if currRGB[0] != lastRGB[0] or currRGB[1] != lastRGB[1] or currRGB[2] != lastRGB[2]:
                  fout.write('\tCOLOR,\t' + str(currRGB[0]) + ',\t' + str(currRGB[1]) + ',\t' + str(currRGB[2]) + ',\n')
               fout.write('\tSPHERE,\t' + str(XYZ[0]) + ',\t' + str(XYZ[1]) + ',\t' + str(XYZ[2]) + ',\t' + str(rad) + ',\n')
         elif typeVertex:
            match = re.search(r'(-?\d\d?\.\d\d)\s+(-?\d\d?\.\d\d)\s+(-?\d\d?\.\d\d)\s+(\d\.\d\d)\s+(\d\.\d\d)\s+(\d\.\d\d)', line)
            if match:
               XYZ[0] = float(match.group(1))
               XYZ[1] = float(match.group(2))
               XYZ[2] = float(match.group(3))
               lastRGB[:] = currRGB[:]
               currRGB[0] = float(match.group(4))
               currRGB[1] = float(match.group(5))
               currRGB[2] = float(match.group(6))

               if currRGB[0] != lastRGB[0] or currRGB[1] != lastRGB[1] or currRGB[2] != lastRGB[2]:
                  fout.write('\tCOLOR,\t' + str(currRGB[0]) + ',\t' + str(currRGB[1]) + ',\t' + str(currRGB[2]) + ',\n')
               fout.write('\tVERTEX,\t' + str(XYZ[0]) + ',\t' + str(XYZ[1]) + ',\t' + str(XYZ[2]) + ',\n')

   fout.write('\t]\n')
   for obj in listElements:
      strObj += obj + ' + '
   fout.write('obj = ' + strObj[:-3] + '\n')
   fout.write('cmd.load_cgo(obj,\'segment\',\t' + str(frame) + ')\n')

   fin.close()
   fout.close()


if __name__ == '__main__':
   #Parse arguments specifying input/output files
   parser = argparse.ArgumentParser(description='Script for converting MicroAVS Geometry File (MGF) to PyMOL CGO script.')
   parser.add_argument('-mgf', required=True)
   parser.add_argument('-seq', required=True)
   parser.add_argument('-static', required=False)
   args = parser.parse_args()
   mgf = str(args.mgf)
   seq = str(args.seq)
   static = str(args.static)
   
   main(mgf, seq, static)