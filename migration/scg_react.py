from vr import VrService
from graph import Dijkstra
from mec.mec import MecAgent
from migration.migration import Migration
from migration.react import REACTApproach
from base_station import BaseStationController

class ScgReact(Migration):

    @classmethod
    def discover_mec(
        self, base_station_set: list, mec_set: list, user: dict, service: VrService, 
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""


        current_base_station = BaseStationController.get_base_station(
            base_station_set, user.current_location
        )

        shortest_latency = float("inf")
        path = []
        for base_station in base_station_set:
            if ( 
                MecAgent.check_deployment(
                    mec_set, base_station.mec_id, service
                )
            ):
                """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
                aux_path, new_latency = Dijkstra.init_algorithm(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    start_node=current_base_station.id,
                    target_node=base_station.id,
                )

                if new_latency <= shortest_latency:
                    path = aux_path
                    shortest_latency = new_latency
            else:
                print('REACT ENABLED!')
                #REACT LOGIC COMES HERE...
                #REACTApproach.solidarity()

        """ we need to take care of the case where there is no more mec available """
        if not path:
            return None

        # print(" -> ".join(path))
        """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
        bs_destination = BaseStationController.get_base_station(
            base_station_set, path[-1]
        )
        return bs_destination.mec_id