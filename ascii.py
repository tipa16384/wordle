data = """

    _      _             _   
   /_\  __| __ _____ _ _| |_ 
  / _ \/ _` \ V / -_| ' |  _|
 /_/ \____,_|\_/\___|_||_\__|
  ___ / _|                   
 / _ |  _|                   
 \_____|      _              
  / __|___ __| |___          
 | (__/ _ / _` / -_)         
  \___\___\__,_\___|         
                             
"""

line_num = 10
for l in data.splitlines():
    print (f"{line_num} PRINT \"{l.rstrip()}\"")
    line_num += 10