# protocol-dev
i want to test various protocols

To start,

uv sync

python src/main.py -c example_configs/config.centralManager.yaml

python src/main.py -c example_configs/config.nodeA.yaml
python src/main.py -c example_configs/config.nodeB.yaml
python src/main.py -c example_configs/config.nodeC.yaml

running above commands you can set up grpc servers.

to request, run this

python send_req.py [initiator] [responder]

example

python send_req.py nodeA nodeB