import pandas as pd
from ollama import OllamaInstance
import pickle

class TradingSimulation:
    def __init__(self):
        self.ollama_instance = OllamaInstance()
        self.df = pd.read_csv('data/LiveData.csv')
        self.serialize_state()

    def serialize_state(self):
        with open('serialized_state.pkl', 'wb') as f:
            pickle.dump({'stock': None, 'last_trade_decision': None}, f)

    def deserialize_state(self):
        try:
            with open('serialized_state.pkl', 'rb') as f:
                self.state = pickle.load(f)
        except FileNotFoundError:
            self.state = {'stock': None, 'last_trade_decision': None}

    def get_new_data(self):
        new_line = pd.read_csv('data.csv', nrows=1).values[0]

        history = self.df.iloc[:-1]

        return {
            'new_data': new_line,
            'history': history,
        }

    def make_trade_decision(self):
        self.deserialize_state()
        data, _ = self.get_new_data()
        prompt = f"New data: {data['new_data']}, History: {data['history'].iloc[:5].values}"
        response = self.ollama_instance.get_response(prompt)

        if response == "Buy":
             trade_decision = 'Buy'
        elif response == "Sell":
             trade_decision = 'Sell'
        elif response in ["Hold", "No change"]:
             trade_decision = 'Hold'
        elif response == "Pass":
            trade_decision = 'Pass'
        else:
            trade_decision = 'Hold'

    print(f"Trade decision: {trade_decision}")
    self.state['last_trade_decision'] = trade_decision
    self.serialize_state()

TradingSimulation().make_trade_decision()




#account for pass and hold
