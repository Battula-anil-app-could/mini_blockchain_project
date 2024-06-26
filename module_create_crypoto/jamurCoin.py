import hashlib
import datetime
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from uuid import uuid4 
from urllib.parse import urlparse

# building our own blockchain calss
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain)+1,
            'age': str(datetime.datetime.now()),
            'proof': proof,
            'transactions': self.transactions,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        self.transactions = []
        return block 
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1 
        check_proof = False 
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:4] == '0000':
                check_proof = True 
            else:
                new_proof += 1 
        return new_proof 
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def add_transcation(self, sender, receiver, amount):
        self.transactions.append({'sender': sender, 'receiver':receiver, amount: 'amount'})

        previous_block = self.get_previous_block()
        return previous_block['index'] + 1 
    

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes 
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'https://{node}/get_chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_valid_chain(chain):
                    longest_chain = chain 
                    max_length = length 
        
        if longest_chain:
            self.chain = longest_chain 
            return True
        return False
    
    def is_valid_chain(self):
        previous_block = self.chain[0]
        block_index = 1 

        while block_index < len(self.chain):

            block = self.chain[block_index]

            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False 

            previous_block = block 
            block_index += 1 
        return True
    
    

# created my web flask app 
    
app = Flask(__name__)
CORS(app, origins="http://localhost:3000")
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

node_adderss = str(uuid4()).replace('-', '')
# created my blockchain object 

blockchain = Blockchain()


# mining blockchain

@app.route("/", methods=["GET"])
def home():
    return "Welcome to the darling Blockchain API", 200

@app.route("/mine_block", methods = ["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    blockchain.add_transcation(sender=node_adderss, receiver="anil", amount=10)
    resopnse = {
        "message": "Successfully mined the block",
        'index': block['index'],
        'age': block['age'],
        'proof': block['proof'],
        'transactions': block['transactions'],
        "previous_hash": block['previous_hash']
    }

    return jsonify(resopnse), 200 

@app.route("/get_chain", methods = ["GET"])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200 

@app.route("/is_valid", methods = ["GET"])
def is_valid():
    is_valid = blockchain.is_valid_chain()
    print(is_valid)
    response = {"message": "all blocks are not valid "}
    if is_valid:
        response  = {"message": "all blocks are valid", 
                     'chain': blockchain.chain,
                     'length': len(blockchain.chain)
                     }
    return jsonify(response), 200

@app.route("/add_transaction", methods = ["POST"])
def add_transaction():
    json_input = request.get_json()

    transations_keys = ['sender', 'receiver', 'amount']

    if not all (key in json_input for key in transations_keys):
        return jsonify({"message": "invalid users"}), 400
    
    index = blockchain.add_transcation(json_input['sender'], json_input['receiver'], json_input['amount'])
    response = {"message": f'your transaction added to the block of {index}'}
    return jsonify(response), 200

@app.route("/add_network", methods = ["POST"])
def add_network():
    json_input= request.get_json()
    nodes = json_input.get('nodes')
    if nodes is None:
        return "error while add network", 400
    for node in nodes:
        blockchain.add_node(node)
    
    response = {"message": "successfully network added", "total_nodes": len(blockchain.nodes)}
    return jsonify(response), 200 

@app.route("/replace_chain", methods = ["GET"])
def replace_chain():
    is_replace_chain = blockchain.replace_chain()
    print(is_valid)
    response = {"message": "all good large chain is now runed"}
    if is_replace_chain:
        response  = {"message": "chain successfully replaced.", 
                     'chain': blockchain.chain,
                     'length': len(blockchain.chain)
                     }
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    