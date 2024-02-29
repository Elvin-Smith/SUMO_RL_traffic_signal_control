
from configs import EXP_CONFIGS
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import dump
from lxml import etree as ET
import os
E = ET.Element

#为XML文件添加合适的缩进
def indent(elem, level=0):
    i = "\n  " + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + ""
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i



class Generate_Net():
    def __init__(self, configs):
        self.configs = configs
        self.file_name=self.configs['file_name']
        self.num_lanes = str(self.configs['num_lanes'])
        self.current_Env_path = os.path.dirname(os.path.abspath(__file__))

        #路网信息初始化
        self.nodes = list()
        self.flows = list()
        self.vehicles = list()
        self.edges = list()
        self.connections = list()

    def specify_node(self):
            nodes = list()
            
            return nodes
    
    def specify_edge(self):
        edges = list()
        
        return edges

    def specify_connection(self):#定义连接器
        connections = list()
        
        return connections

    def specify_flow(self):
        flows = list()
        
        return flows

    def specify_outdata(self):
        outputData = list()
        
        return outputData

    def specify_traffic_light(self):
        traffic_light = list()
        
        return traffic_light

    def _generate_nod_xml(self):
        self.nodes = self.specify_node()
        nod_xml = ET.Element('nodes') #创建根节点

        for node_dict in self.nodes:
            print(node_dict)
            # node_dict['x']=format(node_dict['x'],'.1f')
            nod_xml.append(E('node', attrib=node_dict))
            indent(nod_xml, 1)

        dump(nod_xml)#在终端显示xml文件结构

        tree = ET.ElementTree(nod_xml)#将根目录转化为xml树状结构(即ElementTree对象) 
        
        # tree.write(self.file_name+'.xml',encoding='utf-8',xml_declaration=True)
        tree.write(os.path.join(self.current_Env_path,'network', self.file_name+'.nod.xml'), pretty_print=True,
                   encoding='UTF-8', xml_declaration=True)

    def _generate_edg_xml(self):
        self.edges = self.specify_edge()
        edg_xml = ET.Element('edges')
        
        for _, edge_dict in enumerate(self.edges):
            edg_xml.append(E('edge', attrib=edge_dict))
            indent(edg_xml, 1)
        dump(edg_xml)
        tree = ET.ElementTree(edg_xml)
        # tree.write(self.xml_edg_name+'.xml',encoding='utf-8',xml_declaration=True)
        tree.write(os.path.join(self.current_Env_path,'network', self.file_name+'.edg.xml'), pretty_print=True,
                   encoding='UTF-8', xml_declaration=True)

    def _generate_net_xml(self):
        # file_name_str=os.path.join(self.current_Env_path,self.file_name)
        file_name_str = os.path.join(self.current_Env_path,'network', self.file_name)
        if len(self.traffic_light) != 0:
            os.system('netconvert -n {0}.nod.xml -e {0}.edg.xml -i {0}.tll.xml -o {0}.net.xml --no-turnarounds True'.format(
                file_name_str))
        elif len(self.connections) == 0:
            os.system('netconvert -n {}.nod.xml -e {}.edg.xml -o {}.net.xml --no-turnarounds True'.format(
                file_name_str, file_name_str, file_name_str))
        else:  # connection이 존재하는 경우 -x
            os.system('netconvert -n {}.nod.xml -e {}.edg.xml -x {}.con.xml -o {}.net.xml --no-turnarounds True'.format(
                file_name_str, file_name_str, file_name_str, file_name_str))

    def _generate_rou_xml(self):
        self.flows = self.specify_flow()
        route_xml = ET.Element('routes')
        if len(self.vehicles) != 0:  # empty
            for _, vehicle_dict in enumerate(self.vehicles):
                route_xml.append(E('veh', attrib=vehicle_dict))
                indent(route_xml, 1)
        if len(self.flows) != 0:
            for _, flow_dict in enumerate(self.flows):
                route_xml.append(E('flow', attrib=flow_dict))
                indent(route_xml, 1)
        dump(route_xml)
        tree = ET.ElementTree(route_xml)
        tree.write(os.path.join(self.current_Env_path, self.file_name+'.rou.xml'), pretty_print=True,
                   encoding='UTF-8', xml_declaration=True)

    def _generate_con_xml(self):
        self.cons = self.specify_connection()
        con_xml = ET.Element('connections')
        if len(self.connections) != 0:  # empty
            for _, connection_dict in enumerate(self.connections):
                con_xml.append(E('connection', attrib=connection_dict))
                indent(con_xml, 1)

        dump(con_xml)
        tree = ET.ElementTree(con_xml)
        tree.write(os.path.join(self.current_Env_path,'network', self.file_name+'.con.xml'), pretty_print=True,
                   encoding='UTF-8', xml_declaration=True)

    def _generate_tll_xml(self):
        traffic_light_set = self.specify_traffic_light()
        self.traffic_light = traffic_light_set
        tll_xml = ET.Element('additional')
        if len(self.traffic_light) != 0:
            for _, tl in enumerate(traffic_light_set):
                phase_set = tl.pop('phase')
                tlLogic = ET.SubElement(tll_xml, 'tlLogic', attrib=tl)
                indent(tll_xml, 1)
                for _, phase in enumerate(phase_set):
                    tlLogic.append(E('phase', attrib=phase))
                    indent(tll_xml, 2)
        tree = ET.ElementTree(tll_xml)
        tree.write(os.path.join(self.current_Env_path,'network', self.file_name+'.tll.xml'), pretty_print=True,
                   encoding='UTF-8', xml_declaration=True)
        


    def generate_cfg(self, route_exist, mode='simulate'):
        '''
        if all the generation over, inherit this function by `super`.
        '''
        sumocfg = ET.Element('configuration')
        inputXML = ET.SubElement(sumocfg, 'input')
        inputXML.append(
            E('net-file', attrib={'value': os.path.join(self.current_Env_path, self.file_name+'.net.xml')}))
        indent(sumocfg)
        if route_exist == True:
            if self.configs['network'] == 'grid':  # grid에서만 생성
                self._generate_rou_xml()
            if os.path.exists(os.path.join(self.current_Env_path, self.file_name+'.rou.xml')):
                inputXML.append(
                    E('route-files', attrib={'value': os.path.join(self.current_Env_path, self.file_name+'.rou.xml')}))
                indent(sumocfg)

        # if os.path.exists(os.path.join(self.current_Env_path, self.file_name+'_data.add.xml')):
        #     inputXML.append(
        #         E('additional-files', attrib={'value': os.path.join(self.current_Env_path, self.file_name+'_data.add.xml')}))
        #     indent(sumocfg)
        inputXML.append(E('additional-files', attrib={'value': os.path.join(self.current_Env_path, self.file_name+'_data.add.xml')}))
        indent(sumocfg)

        time = ET.SubElement(sumocfg, 'time')
        time.append(E('begin', attrib={'value': str(self.sim_start)}))
        indent(sumocfg)
        time.append(E('end', attrib={'value': str(self.max_steps)}))
        indent(sumocfg)
        outputXML = ET.SubElement(sumocfg, 'output')
        indent(sumocfg)
        dump(sumocfg)
        tree = ET.ElementTree(sumocfg)
        if mode == 'simulate':
            tree.write(os.path.join(self.current_Env_path, self.file_name+'_simulate.sumocfg'),
                       pretty_print=True, encoding='UTF-8', xml_declaration=True)
        elif mode == 'test':
            tree.write(os.path.join(self.current_Env_path, self.file_name+'_test.sumocfg'),
                       pretty_print=True, encoding='UTF-8', xml_declaration=True)
        elif mode == 'train' or mode == 'train_old':
            tree.write(os.path.join(self.current_Env_path, self.file_name+'_train.sumocfg'),
                       pretty_print=True, encoding='UTF-8', xml_declaration=True)

    def test_net(self):
        self.generate_cfg(False)

        os.system('sumo-gui -c {}.sumocfg'.format(os.path.join(self.current_Env_path,
                                                               self.file_name+'_simulate')))

    def sumo_gui(self):
        self.generate_cfg(True)
        os.system('sumo-gui -c {}.sumocfg'.format(
            os.path.join(self.current_Env_path, self.file_name+'_simulate')))

    def generate_all_xml(self):
        self._generate_nod_xml()
        self._generate_edg_xml()
        self._generate_tll_xml()
        self._generate_net_xml()
        self._generate_rou_xml()

class Grid_Net(Generate_Net):
    def __init__(self,grid_num,configs):
        super().__init__(configs)
        self.grid_num = grid_num
        
        
        
    
    def specify_node(self):
        nodes = list()
        center = float(self.grid_num)/2.0
        for x in range(self.grid_num):
            for y in range(self.grid_num):
                node_info = dict()
                # tl表示交通信号灯ID ，相同ID会被在控制时编入相同的组
                node_info = {
                    'id': 'n_'+str(x)+'_'+str(y),
                    'type': 'traffic_light',
                    'tl': 'n_'+str(x)+'_'+str(y),
                }
                # if self.grid_num % 2==0: # odd due to index rule
                #     grid_x=self.configs['laneLength']*(x-center_x)
                #     grid_x=self.configs['laneLength']*(center_y-y)

                # else: # even due to in dex rule
                grid_x = self.configs['laneLength']*(x-center)
                grid_y = self.configs['laneLength']*(center-y)

                node_info['x'] = str('%.1f' % grid_x)
                node_info['y'] = str('%.1f' % grid_y)
                nodes.append(node_info)
                #self.tl_rl_list.append(node_info)
        for i in range(self.grid_num):
            grid_y = (center-i)*self.configs['laneLength']
            grid_x = (i-center)*self.configs['laneLength']
            node_information = [{
                'id': 'n_'+str(i)+'_u',
                'x': str('%.1f' % grid_x),
                'y': str('%.1f' % (-center*self.configs['laneLength']+(self.grid_num+1)*self.configs['laneLength']))
            },
                {
                'id': 'n_'+str(i)+'_r',
                'x': str('%.1f' % (-center*self.configs['laneLength']+(self.grid_num)*self.configs['laneLength'])),
                'y':str('%.1f' % grid_y)
            },
                {
                'id': 'n_'+str(i)+'_d',
                'x': str('%.1f' % grid_x),
                'y': str('%.1f' % (+center*self.configs['laneLength']-(self.grid_num)*self.configs['laneLength']))
            },
                {
                'id': 'n_'+str(i)+'_l',
                'x': str('%.1f' % (+center*self.configs['laneLength']-(self.grid_num+1)*self.configs['laneLength'])),
                'y':str('%.1f' % grid_y)
            }]
            for _, node_info in enumerate(node_information):
                nodes.append(node_info)
        self.configs['node_info'] = nodes
        self.nodes = nodes
        return nodes

    def specify_edge(self):
        edges = list()
        edges_dict = dict()
        for i in range(self.grid_num):
            edges_dict['n_{}_l'.format(i)] = list()
            edges_dict['n_{}_r'.format(i)] = list()
            edges_dict['n_{}_u'.format(i)] = list()
            edges_dict['n_{}_d'.format(i)] = list()

        for y in range(self.grid_num):
            for x in range(self.grid_num):
                edges_dict['n_{}_{}'.format(x, y)] = list()

                # outside edge making
                if x == 0:
                    edges_dict['n_{}_{}'.format(x, y)].append(
                        'n_{}_l'.format(y))
                    edges_dict['n_{}_l'.format(y)].append(
                        'n_{}_{}'.format(x, y))
                if y == 0:
                    edges_dict['n_{}_{}'.format(x, y)].append(
                        'n_{}_u'.format(x))
                    edges_dict['n_{}_u'.format(x)].append(
                        'n_{}_{}'.format(x, y))
                if y == self.grid_num-1:
                    edges_dict['n_{}_{}'.format(x, y)].append(
                        'n_{}_d'.format(x))
                    edges_dict['n_{}_d'.format(x)].append(
                        'n_{}_{}'.format(x, y))
                if x == self.grid_num-1:
                    edges_dict['n_{}_{}'.format(x, y)].append(
                        'n_{}_r'.format(y))
                    edges_dict['n_{}_r'.format(y)].append(
                        'n_{}_{}'.format(x, y))

                # inside edge making
                if x+1 < self.grid_num:
                    edges_dict['n_{}_{}'.format(x, y)].append(
                        'n_{}_{}'.format(x+1, y))

                if y+1 < self.grid_num:
                    edges_dict['n_{}_{}'.format(x, y)].append(
                        'n_{}_{}'.format(x, y+1))
                if x-1 >= 0:
                    edges_dict['n_{}_{}'.format(x, y)].append(
                        'n_{}_{}'.format(x-1, y))
                if y-1 >= 0:
                    edges_dict['n_{}_{}'.format(x, y)].append(
                        'n_{}_{}'.format(x, y-1))

        for _, dict_key in enumerate(edges_dict.keys()):
            for i, _ in enumerate(edges_dict[dict_key]):
                edge_info = dict()
                edge_info = {
                    'from': dict_key,
                    'id': "{}_to_{}".format(dict_key, edges_dict[dict_key][i]),
                    'to': edges_dict[dict_key][i],
                    'numLanes': self.num_lanes
                }
                edges.append(edge_info)
        self.edges = edges
        self.configs['edge_info'] = edges
        return edges
    
    def specify_connection(self):
        connections = list()

        self.connections = connections
        return connections
    
    def specify_traffic_light(self):
        traffic_lights = []
        num_lanes = self.configs['num_lanes']
        g = 'G'
        r = 'r'
        for i in range(self.grid_num):
            for j in range(self.grid_num):

                # 按照【北进口-东进口-南进口-西进口】的顺序设置
                # 每个进口按照【右转-直行-左转】顺序排序
                # 同一个进口同一个转向的按照【从右到左的车道】排序


                # 对于一个经典的四个路口的道路，只考虑存在三条车道，正反方向都有，右拐不受限制，那就只剩下8个方向
                phase_set = [
                    {'duration': '20',  # 1
                     'state': 'r{2}{1}r{2}{3}r{2}{1}r{2}{3}'.format(  # 위좌아래좌
                         g*num_lanes, g, r*num_lanes, r),
                     },
                    {'duration': '3',
                     'state': 'y'*(8+4*num_lanes),
                     },
                    # {'duration': '3',
                    #  'state': 'r'*(8+4*num_lanes),
                    #  },
                    {'duration': '20',  # 2
                     'state': 'G{0}{3}r{2}{3}G{0}{3}r{2}{3}'.format(  # 위직아래직
                         g*num_lanes, g, r*num_lanes, r),  # current
                     },
                    {'duration': '3',
                     'state': 'y'*(8+4*num_lanes),
                     },
                    # {'duration': '3',
                    #  'state': 'r'*(8+4*num_lanes),
                    #  },
                    {'duration': '20',  # 1
                     'state': 'r{2}{3}r{2}{1}r{2}{3}r{2}{1}'.format(  # 좌좌우좌
                         g*num_lanes, g, r*num_lanes, r),
                     },
                    {'duration': '3',
                     'state': 'y'*(8+4*num_lanes),
                     },
                    # {'duration': '3',
                    #  'state': 'r'*(8+4*num_lanes),
                    #  },
                    {'duration': '20',  # 1
                     'state': 'r{2}{3}G{0}{3}r{2}{3}G{0}{3}'.format(  # 좌직우직
                         g*num_lanes, g, r*num_lanes, r),  # current
                     },
                    {'duration': '3',
                     'state': 'y'*(8+4*num_lanes),
                     },
                    # {'duration': '3',
                    #  'state': 'r'*(8+4*num_lanes),
                    #  },
                ]
                
                # 2행시
                # phase_set = [
                #     {'duration': '42',
                #      'state': 'G{}ggr{}rrG{}ggr{}rr'.format('G'*num_lanes, 'r'*num_lanes, 'G'*num_lanes, 'r'*num_lanes),
                #      },
                #     {'duration': '3',
                #      'state': 'y{}yyr{}rry{}yyr{}rr'.format('y'*num_lanes, 'r'*num_lanes, 'y'*num_lanes, 'r'*num_lanes),
                #      },
                #     {'duration': '42',
                #      'state': 'r{}rrG{}ggr{}rrG{}gg'.format('r'*num_lanes, 'G'*num_lanes, 'r'*num_lanes, 'G'*num_lanes),
                #      },
                #     {'duration': '3',
                #      'state': 'r{}rry{}yyr{}rry{}yy'.format('r'*num_lanes, 'y'*num_lanes, 'r'*num_lanes, 'y'*num_lanes),
                #      },
                # ]
                traffic_lights.append({
                    'id': 'n_{}_{}'.format(i, j),
                    'type': 'static',
                    'programID': 'n_{}_{}'.format(i, j),
                    'offset': '0',
                    'phase': phase_set,
                })
        # rl_phase_set = [
        #     {'duration': '35',  # 1
        #      'state': 'r{2}{1}gr{2}{3}rr{2}{1}gr{2}{3}r'.format(  # 위좌아래좌
        #          g*num_lanes, g, r*num_lanes, r),
        #      },
        #     {'duration': '5',
        #      'state': 'y'*20,
        #      },
        #     {'duration': '35',  # 2
        #      'state': 'G{0}{3}rr{2}{3}rG{0}{3}rr{2}{3}r'.format(  # 위직아래직
        #          g*num_lanes, g, r*num_lanes, r),  # current
        #      },
        #     {'duration': '5',
        #      'state': 'y'*20,
        #      },
        #     {'duration': '35',  # 1
        #      'state': 'r{2}{3}rr{2}{1}gr{2}{3}rr{2}{1}g'.format(  # 좌좌우좌
        #          g*num_lanes, g, r*num_lanes, r),
        #      },
        #     {'duration': '5',
        #      'state': 'y'*20,
        #      },
        #     {'duration': '35',  # 1
        #      'state': 'r{2}{3}rG{0}{3}rr{2}{3}rG{0}{3}g'.format(  # 좌직우직
        #          g*num_lanes, g, r*num_lanes, r),  # current
        #      },
        #     {'duration': '5',
        #      'state': 'y'*20,
        #      },
        # ]
        # traffic_lights.append({
        #     'id': 'n_1_1',
        #     'type': 'static',
        #     'programID': 'n_1_1',
        #     'offset': '0',
        #     'phase': rl_phase_set,
        # })
        return traffic_lights

if __name__ == "__main__":
    grid_num=5
    configs = EXP_CONFIGS
    configs['grid_num'] = grid_num
    grid=Grid_Net(grid_num,configs)
    grid._generate_nod_xml()
    grid._generate_edg_xml()
    grid._generate_tll_xml()
    grid._generate_net_xml()
    

