""" munch dictionaries module """
from munch import DefaultMunch

""" np incoder module"""
from encoders.json_encoder import JsonEncoder

""" importing vr module """
from vr.vr import VrService
from vr.vr_controller import VrController

""" import base station module """
from base_station.bs_controller import BaseStationController

""" import mec modules """
from mec.mec import Mec, MecAgent, MecResourceController

""" import graph modules """
from graph.graph import Dijkstra

""" other modules """
from pprint import pprint
import json
import os


class MecController:
    """ represents a MEC controller for MEC servers """

    @staticmethod
    def load_mec_servers() -> dict:
        print("*** loading mec servers ***")
        files_directory = "./mec/"
        file_name_servers = "mecs.txt"
        with open("{}{}".format(files_directory, file_name_servers)) as json_file:
            data = json.loads(json_file.read())
            result = DefaultMunch.fromDict(data)
            return result

    @staticmethod
    def discover_mec(
        base_station_set: list, mec_set: list, user: dict, service: VrService, 
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""


        current_base_station = BaseStationController.get_base_station(
            base_station_set, user.current_location
        )

        if MecAgent.check_deployment(
            mec_set=mec_set, mec_id=current_base_station.mec_id, service=service
        ):
            """ mec server attached to the base station where the user is connected can deploy the vr service """
            return current_base_station.mec_id

        else:
            """ otherwise, we need to look for nearby mec server """

            best_destination = ""
            shortest_latency = float("inf")
            for link in current_base_station.links:
                bs_destination = BaseStationController.get_base_station(
                    base_station_set, link.dst.device
                )
                if MecAgent.check_deployment(mec_set, bs_destination.mec_id, service):
                    """ we need to take care of the network latency """
                    if link.latency < shortest_latency:
                        best_destination = bs_destination.id

            if best_destination != "":
                """ a nearby mec can deploy the service """
                bs_destination = BaseStationController.get_base_station(
                    base_station_set, best_destination
                )
                return bs_destination.mec_id
            else:
                """ otherwise, we should call Dijkstra algorithm for all nodes. The initial node is where the user is connected """
                shortest_latency = float("inf")
                path = []
                for base_station in base_station_set:
                    if (
                        base_station.id != current_base_station.id
                        and MecAgent.check_deployment(
                            mec_set, base_station.mec_id, service
                        )
                    ):
                        """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
                        src_bs = BaseStationController.get_base_station(
                            base_station_set, current_base_station.id
                        )
                        src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
                        aux_path, new_latency = Dijkstra.init_algorithm(
                            base_station_set=base_station_set,
                            mec_set=mec_set,
                            start_node=current_base_station.id,
                            start_node_computing_delay=src_mec.computing_latency,
                            target_node=base_station.id,
                        )

                        if new_latency <= shortest_latency:
                            path = aux_path
                            shortest_latency = new_latency

                """ we need to take care of the case where there is no more mec available """
                if not path:
                    return None

                # print(" -> ".join(path))
                """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
                bs_destination = BaseStationController.get_base_station(
                    base_station_set, path[-1]
                )
                return bs_destination.mec_id

    @staticmethod
    def init_static_services(mec_set: list, mec: Mec) -> None:
        """ creates services that will be deployed on mec server i """
        while True:
            """ checks if mec i has gpu resources """
            cpu_only = False
            if mec.overall_gpu == 0:
                cpu_only = True

            new_service = VrService(cpu_only=cpu_only)

            if MecAgent.available_resources(mec_set, mec.id, new_service):
                MecAgent.deploy_service(mec_set, mec.id, new_service)
            else:
                break

    @staticmethod
    def init_servers(overall_mecs: int) -> None:
        """ first of all, clean devices and hosts on onos sdn controller """

        files_directory = "./mec/"
        file_name_servers = "mecs.txt"

        if os.path.isfile("{}{}".format(files_directory, file_name_servers)):
            return

        """ init mec servers and vr services """
        mec_set = []

        """ generates cpu and gpu resources for all mec servers """
        resource_controller = MecResourceController()
        cpu_set = resource_controller.generate_cpu_resources(overall_mecs)
        gpu_set = resource_controller.generate_gpu_resources(overall_mecs)

        for i in range(0, overall_mecs):
            """ creating mec server i """
            overall_mec_cpu = cpu_set[i]
            overall_mec_gpu = gpu_set[i]
            new_mec = DefaultMunch.fromDict(Mec(overall_mec_cpu, overall_mec_gpu))

            """ stores mec server on scg controller's mec set """
            mec_set.append(new_mec)

        """ instantiating services on each mec server """
        for mec in mec_set:
            MecController.init_static_services(mec_set=mec_set, mec=mec)

        """ transforming mecs to dict """
        new_mec_set = []
        for mec in mec_set:
            new_mec_set.append(mec.to_dict())
        mec_set = new_mec_set

        # a = input("")
        """ encoding json to txt file """
        JsonEncoder.encoder(mec_set, files_directory, file_name_servers)

    @staticmethod
    def get_mec(mec_set: list, mec_id: str) -> Mec:
        """ returns a MEC server """
        for mec in mec_set:
            if mec.id == mec_id:
                return mec

    @staticmethod
    def print_mecs(base_station_set: list, mec_set: list):
        print("\n###############  LISTING MECS ###################\n")
        for base_station in base_station_set:

            mec = MecController.get_mec(mec_set, base_station.mec_id)
            print("BS: {}".format(base_station.id))
            print("ID: {}".format(mec.id))
            print(
                "CPU: {} | ALOCATED CPU: {}".format(mec.overall_cpu, mec.allocated_cpu)
            )
            print(
                "GPU: {} | ALLOCATED GPU: {}".format(mec.overall_gpu, mec.allocated_gpu)
            )
            """
            print("LATENCY: {}".format(mec.computing_latency))
            print("Services:")
            for service in mec.services_set:
                print(service.id)
            """
            print("-------------------------------")
        print("################    END     ##################\n")

    """ NEED TO BE TESTED! """
    """ THIS METHOD COULD BE REWRITEN CONSIDERING A SINGLE INSTANCE OF A FATHER CLASS FOR MIFRATION ALGORITHMS  """

