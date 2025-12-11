# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
from pathlib import Path

import sys
import os
import re

from pathlib import Path

lib_path = str(Path(__file__).parent / "lib")
if lib_path not in sys.path:
    sys.path.append(lib_path)

import dronecan

def find_files_by_number(target_number):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.join(script_dir, 'dsdl_specs')
    matched_files = []
    pattern = re.compile(rf'^{target_number}\..+')

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if pattern.match(filename):
                matched_files.append(os.path.join(dirpath, filename))

    if not matched_files:
        return "whoops"
    filename = os.path.basename(matched_files[0])  
    parts = filename.split('.')  
    return parts[1]

def reverse_bits_16bit(x):
    result = 0
    for i in range(16):
        if (x >> i) & 1:
            result |= 1 << (15 - i)
    return result

class Hla(HighLevelAnalyzer):

    result_types = {
    'Standard Message': {
        'format': 'Standard Msg, Priority: {{data.Priority}}, Src: {{data.Source_ID}}, Name: {{data.Name}}, TypeID: {{data.Message_Data}}'
    },
    'Request Message': {
        'format': 'Request Msg, Priority: {{data.Priority}}, Src: {{data.Source_ID}}, Dest: {{data.Destination_Node_ID}}, Name: {{data.Name}}, TypeID: {{data.Message_Data}}'
    },
    'Response Message': {
        'format': 'Response Msg, Priority: {{data.Priority}}, Src: {{data.Source_ID}}, Dest: {{data.Destination_Node_ID}}, Name: {{data.Name}}, TypeID: {{data.Message_Data}}'
    },
    'Anonymous Message': {
        'format': 'Anonymous Msg, Priority: {{data.Priority}}, Name: {{data.Name}}, TypeID: {{data.Message_Data}}, Discr: {{data.Discriminator}}'
    },
    'Unknown Message Type': {
        'format': 'Unknown Msg'
    },
    'Not Identifier': {
        'format': 'Not Identifier'
    },
    'Not Extended': {
        'format': 'Not Extended'
    },
    'Acknowledgement': {
        'format': 'Acknowledgement'
    },
    'CRC': {
        'format': 'CRC'
    },
    'Extended': {
        'format': 'Extended, Priority: {{data.Priority}}, Source Node ID: {{data.Source_ID}}'
    },
    'Ctrl':{
        'format': 'Control, Num of Bytes: {{data.numbytes}}'
    },
    'Data':{
        'format': 'Data'
    },
    'Full-Frame':{
        'format': 'Full Msg, Name: {{data.Name}}, Data: {{data.Data}}'
    },
    'Msg':{
        'format': 'Control, Num of Bytes: {{data.numbytes}}'
    }
}
    

    def __init__(self):

        self.number_of_data_frames = None
        self.numb_msgs = None
        self.current_full_msg = None
        self.frame_start = None
        self.frame_end = None
        self.message_start = None
        self.message_end = None
        self.current_end = None
        self.last_message = True
        self.multi_message = None
        self.started = False
        self.name = None
        self.data = []
        self.frames = []
        self.id = None


    def decode(self, frame: AnalyzerFrame):
        if frame.type == 'identifier_field':
            
            #print("checking if extended")
            if 'extended' in frame.data and frame.data['extended']:
                
                
                if(self.last_message):
                    self.frames = []
                    self.last_message = False
                if(self.id != frame.data['identifier']):
                    self.frames =[]
                self.data = []
                self.frame_start = frame.start_time
                self.number_of_data_frames = 0
                value = frame.data['identifier']
                self.id = value
                #reads the first 5 bits of the identifier
                current_service = value >> 7 & 0x01       
                #reads the service not bit 
                current_source_node_id = value & 0x7F      
                current_priority = value >> 24 & 0x1F  
                
                if not current_service and current_source_node_id:
                    current_message_data = value >> 8 & 0xFFFF
                    string = find_files_by_number(current_message_data)
                    
                    current_message_type = 'Standard Message'

                elif current_service and current_source_node_id:
                    current_message_data = value >> 16 & 0xFF
                    current_destination_node_id = value >> 8 & 0x7F
                    string = find_files_by_number(current_message_data)
                    if value >> 15 & 0x01:
                        current_message_type = 'Request Message'

                    else:
                        current_message_type = 'Response Message'

                elif not current_service and current_source_node_id == 0:
                    #reads the data type id, which is the next 7 bits after the service not bit
                    current_message_data = value >> 8 & 0x3
                    current_message_type = 'Anonymous Message'
                    current_discriminator = value >> 10 & 0x3FFF
                    string = find_files_by_number(current_message_data)
                    
                
                else: 
                    current_message_data = None
                    current_message_type = 'Unknown Message Type'
                self.name = string
                    

        if frame.type == 'control_field':
            #num = frame.data['num_data_bytes']
            #self.data.append(num)
            self.numb_msgs = frame.data['num_data_bytes']

        if frame.type == 'data_field':
            num = frame.data['data']
            self.data.append(int.from_bytes(num, "little"))
            self.number_of_data_frames = self.number_of_data_frames + 1
            if(self.number_of_data_frames == 8):
                if(int.from_bytes(num,"big") & 0b10000000):
                    self.message_start = self.frame_start
                    self.started = True
                if(int.from_bytes(num,"big") & 0b1000000):
                    self.last_message = True
            elif(self.numb_msgs == self.number_of_data_frames):
                if(int.from_bytes(num,"big") & 0b10000000):
                    self.message_start = self.frame_start
                    self.started = True
                self.last_message = True
            

        if frame.type == 'crc_field':
            fn = 2
        if frame.type == 'ack_field':

            self.frames.append(dronecan.transport.Frame(
                    message_id = self.id,
                    data = self.data,
                    
                    ts_real = 0,
                    canfd = False
                ))
            if(self.last_message and self.started):
                T = dronecan.transport.Transfer()
                
                try: 
                    T.from_frames(self.frames)
                    value = dronecan.to_yaml(T.payload)
                    
                    
                except Exception:
                    value = "Exception occured :("
                self.multi_message = False
                self.started = False
                return AnalyzerFrame('Full-Frame',self.message_start, frame.end_time,{
                    'Name' : self.name,
                    'Data' : value
                })

        
