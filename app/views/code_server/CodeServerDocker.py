import os
from pathlib import Path

import docker
from docker.errors import NotFound
from docker.models.containers import Container

from Config import globalConfig

from exceptions.DockerException import NotRunning
from utils.Singleton import Singleton


class CodeServerDocker(metaclass=Singleton):
    network_name = globalConfig.docker_network.lower()
    container_name_prefix = "code-server_"

    def __init__(self):
        self.client = docker.from_env()

    def create_code_server(self, user_name: str):
        code_server_volumes_dir = Path(globalConfig.DOCKER_CODE_SERVER_DIR) / user_name
        asset_dirs = Path(globalConfig.geoserver_data_dir) / "data" / user_name
        code_server_passwd = "123456"
        return self.client.containers.run('deepgis_codeserver:0.1.2',
                                          detach=True,
                                          name=f'{self.container_name_prefix}{user_name}',
                                          network=self.network_name,
                                          volumes={
                                              code_server_volumes_dir: {'bind': '/home/coder',
                                                                        'mode': 'rw'},
                                              asset_dirs: {'bind': '/home/coder/assets',
                                                           "mode": "ro"}
                                          },
                                          environment={'PASSWORD': code_server_passwd,
                                                       'db_user': os.environ.get('postgis_db_user'),
                                                       'db_pass': os.environ.get('postgis_db_passwd')},
                                          ports={'8080/tcp': None},
                                          user='root')

    def _get_container(self, user_name: str):
        container_name = f"{self.container_name_prefix}{user_name}"
        return self.client.containers.get(container_name)

    def get_code_server_url(self, user_name: str):
        container = self._get_container(user_name)
        if container.status != "running":
            raise NotRunning("")
        port = self._get_container_host_port(container)
        return self._join_url(port)

    def get_or_create_container_url(self, user_name: str) -> str:
        """
        基于用户名获取container的访问地址，如果不存在容器，则创建并返回
        :param user_name:
        :return:
        """
        try:
            url = self.get_code_server_url(user_name=user_name)
        except NotRunning:
            container = self._get_container(user_name)
            container.start()
            url = self.get_code_server_url(user_name=user_name)
        except NotFound:
            container = self.create_code_server(user_name=user_name)
            port = self._get_container_host_port(container)
            url = self._join_url(port)
        return url

    @staticmethod
    def _join_url(port, host=globalConfig.server_host):
        """
        返回url和端口号拼接后的结果
        :param port:
        :return:
        """
        return "http://" + host + ":" + str(port)

    def _get_container_host_port(self, container: Container) -> int:
        """
        根据container获取其8080端口的宿主机映射端口
        :param container: 容器对象
        :return: [{"HostIp":"0.0.0.0","HostPort":port},...]
        """
        container_id_s = container.short_id
        port_list = self.client.api.port(container_id_s, 8080)
        return port_list[0]['HostPort']


codeServerDocker = CodeServerDocker()
if __name__ == '__main__':
    container_url = codeServerDocker.get_or_create_container_url('test')
    print(container_url)
    # pass
