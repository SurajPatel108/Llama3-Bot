import pandas as pd
import pickle
import ollama
from pathlib import Path
from datetime import datetime
from alpaca_trade_api import REST

API_KEY = 'PKZJLPPXZNYRB9CDAV2P'
API_SECRET = 'LDY1oZ65VOtnAxaRDoi0ejX3ZBupRwmn8qbI7uLr'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

api = REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

amount = 0.02

class TradingSimulation:
    def __init__(self):
        self.data_file = Path('data/liveData.csv')
        self.state_file = Path('serialized_state.pkl')
        self.instruction_file = Path('ai_instructions.txt')
        self.load_data()
        self.deserialize_state()
        self.load_instructions()

    def load_data(self):
        try:
            self.df = pd.read_csv(self.data_file)
        except FileNotFoundError:
            print(f"Error: {self.data_file} not found.")
            self.df = pd.DataFrame()

    def load_instructions(self):
        try:
            with self.instruction_file.open('r') as f:
                self.instructions = f.read()
        except FileNotFoundError:
            print(f"Error: {self.instruction_file} not found.")
            self.instructions = "Analyze the data and respond with Buy, Sell, Hold, or Pass."

    def serialize_state(self, trade_decision):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_state = {'timestamp': current_time, 'decision': trade_decision}

        try:
            with self.state_file.open('rb') as f:
                existing_states = pickle.load(f)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            existing_states = []

        existing_states.append(new_state)

        with self.state_file.open('wb') as f:
            pickle.dump(existing_states, f)

    def deserialize_state(self):
        if self.state_file.exists():
            try:
                with self.state_file.open('rb') as f:
                    self.traderbot_state = pickle.load(f)
            except (EOFError, pickle.UnpicklingError):
                print(f"Warning: {self.state_file} is empty or corrupted. Initializing new state.")
                self.traderbot_state = []
        else:
            self.traderbot_state = []

    def get_new_data(self):
        if not self.df.empty:
            new_line = self.df.tail(1).values[0]
            history = self.df.iloc[:-1]
        else:
            new_line = []
            history = pd.DataFrame()

        return {
            'new_data': new_line,
            'history': history,
        }

    def make_trade_decision(self):
        data = self.get_new_data()
        trading_history = "\n".join(
            [f"{state['timestamp']}: {state['decision']}" for state in self.traderbot_state])  # Last 5 decisions

        prompt = f"""{self.instructions}

New data: {data['new_data']}
History: {data['history']}

Your recent trading history:
{trading_history}

Based on this information, what is your trading decision?"""

        try:
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'user', 'content': prompt}
                ]
            )

            print(f"Ollama says: {response['message']['content']}")

            decision = response['message']['content'].strip().lower()

            if decision == "buy":
                trade_decision = 'Buy'

                buy_order = api.submit_order(
                    symbol='BTCUSD',
                    qty=amount,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                print("Buy Order Response:", buy_order)

            elif decision == "sell":
                trade_decision = 'Sell'

                sell_order = api.submit_order(
                    symbol='BTCUSD',
                    qty=amount,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                print("Sell Order Response:", sell_order)

            elif decision == "hold":
                trade_decision = 'Hold'
            elif decision == "pass":
                trade_decison = 'Pass'
            else:
                trade_decision = 'No visible decision made'

            self.serialize_state(trade_decision)

        except Exception as e:
            print(f"An error occurred while making a trade decision: {e}")

if __name__ == "__main__":
    TradingSimulation().make_trade_decision()
