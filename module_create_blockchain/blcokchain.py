import hashlib
import datetime
import json
from flask import Flask, jsonify
from flask_cors import CORS

# building our own blockchain calss
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain)+1,
            'age': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
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
    
    def mine_block(self):
        previous_block = blockchain.get_previous_block()
        previous_proof = previous_block['proof']
        proof = blockchain.proof_of_work(previous_proof)
        previous_hash = blockchain.hash(previous_block)
        block = blockchain.create_block(proof, previous_hash)
        resopnse = {
            "message": "Successfully mined the block",
            'index': block['index'],
            'age': block['age'],
            'proof': block['proof'],
            "previous_hash": block['previous_hash']
        }

blockchain = Blockchain()
blockchain.mine_block()
blockchain.mine_block()
print(blockchain.is_valid_chain())
    
# created my web flask app 
    
app = Flask(__name__)
CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
# created my blockchain object 

blockchain = Blockchain()
blockchain.mine_block()
blockchain.mine_block()
print(blockchain.is_valid_chain())

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
    resopnse = {
        "message": "Successfully mined the block",
        'index': block['index'],
        'age': block['age'],
        'proof': block['proof'],
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
        response  = {"message": "all blaocks are valid", 
                     'chain': blockchain.chain,
                     'length': len(blockchain.chain)
                     }
    return jsonify(response), 200


app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    