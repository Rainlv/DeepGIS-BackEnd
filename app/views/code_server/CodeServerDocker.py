from pathlib import Path
from typing import Dict, List

import docker
from docker.models.containers import Container

from Config import globalConfig, rootDir

# tls_config = docker.tls.TLSConfig(client_cert=(rootDir.joinpath('keys/cert.pem'), rootDir.joinpath('keys/key.pem')),
#                                   ca_cert=rootDir.joinpath('keys/ca.pem'), verify=True)
# client = docker.DockerClient(base_url=globalConfig.DOCKER_BASE_URL, version='auto',
#                              tls=tls_config)

network_name = "gis301_default"
container_name_prefix = "code-server_"


class CodeServerDocker:
    def __init__(self):
        tls_config = docker.tls.TLSConfig(
            client_cert=(rootDir.joinpath('keys/cert.pem'), rootDir.joinpath('keys/key.pem')),
            ca_cert=rootDir.joinpath('keys/ca.pem'), verify=True)
        self.client = docker.DockerClient(base_url=globalConfig.DOCKER_BASE_URL, version='auto',
                                          tls=tls_config)

    def create_code_server(self, user_name: str):
        if not globalConfig.DEBUG:
            code_server_volumes_dir = str(Path(globalConfig.DOCKER_CODE_SERVER_DIR).joinpath(user_name))
        else:
            code_server_volumes_dir = globalConfig.DOCKER_CODE_SERVER_DIR + user_name
        code_server_passwd = "wxh172706002"
        return self.client.containers.run('codercom/code-server',
                                          detach=True,
                                          name=f'{container_name_prefix}{user_name}',
                                          network=network_name,
                                          volumes={
                                              code_server_volumes_dir: {'bind': '/home/coder',
                                                                        'mode': 'rw'}, },
                                          environment={'PASSWORD': code_server_passwd},
                                          ports={'8080/tcp': None},
                                          # restart_policy={"Name": "always", "MaximumRetryCount": 5},
                                          user='root')

    def get_code_server_url(self, user_name: str):
        container_name = f"{container_name_prefix}{user_name}"
        container = self.client.containers.get(container_name)
        container_port_list = self._get_container_host_port(container)
        port = self._get_port_from_portList(container_port_list)
        return

    def _get_container_host_port(self, container: Container) -> List[Dict[str, str]]:
        """
        根据container获取其8080端口的宿主机映射端口
        :param container: 容器对象
        :return: [{"HostIp":"0.0.0.0","HostPort":port},...]
        """
        container_id_s = container.short_id
        return self.client.api.port(container_id_s, 8080)

    @staticmethod
    def _get_port_from_portList(port_list: List[Dict[str, str]]) -> str:
        return port_list[0]['HostPort']


if __name__ == '__main__':
    # docker_instance = CodeServerDocker()
    # container = docker_instance.create_code_server('test')
    # docker_instance.get_code_server_url(container)
    pass
