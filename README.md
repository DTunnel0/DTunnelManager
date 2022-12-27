# DTunnelManager

## Modo de instalacao manual

* Instalando GIT 

```
sudo apt-get update && sudo apt-get install git -y
```

* Instalando script
```
git clone https://github.com/DTunnel0/DTunnelManager.git
cd DTunnelManager
pip3 install -r requirements.txt
```

* Execute o script
```
python3 -m app
```

## Modo de instalacao automatizada

* Instalando python3, pip3 e git
```
sudo apt-get update && sudo apt-get install git python3 python3-pip -y
``` 

* Instalando script
```
pip3 install git+https://github.com/DTunnel0/DTunnelManager.git
```
#### Ou
```
git clone https://github.com/DTunnel0/DTunnelManager.git
cd DTunnelManager
python3 setup.py install
```

## Atualize o script
```
pip3 install --upgrade git+https://github.com/DTunnel0/DTunnelManager.git
```
#### Ou
```
cd ~/
rm -rf DTunnelManager
git clone git+https://github.com/DTunnel0/DTunnelManager.git
cd DTunnelManager
python3 setup.py install
```

* Comando de execucao
```
vps
```