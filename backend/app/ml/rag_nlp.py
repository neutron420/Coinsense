"""
RAG (Retrieval-Augmented Generation) Chatbot for Cryptocurrency Knowledge
"""
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import json
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime
import re
import requests
import httpx

# --- THE CRUCIAL FIX ---
# This line correctly imports your API keys and other settings.
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class CryptoRAGChatbot:
    """RAG-based chatbot for cryptocurrency knowledge"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = None, data_path: str = None):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.data = []  # Correctly initialized attribute
        self.coin_definitions = {
            'BTC': "Bitcoin (BTC) is the first decentralized cryptocurrency. It uses Proof of Work to secure a permissionless network where anyone can validate and transmit transactions. Its primary use is as a scarce digital money and settlement network.",
            'ETH': "Ethereum (ETH) is a smart‑contract platform that moved from Proof of Work to Proof of Stake. It enables programmable money and applications (DeFi, NFTs, DAOs) through the EVM and a rich developer ecosystem.",
            'SOL': "Solana (SOL) is a high‑throughput Layer‑1 blockchain that combines Proof of Stake with Proof of History. It focuses on speed and low fees for consumer apps, DeFi, and NFTs, supported by a parallelized runtime (Sealevel).",
            'ADA': "Cardano (ADA) is a research‑driven PoS blockchain emphasizing formal verification and gradual upgrades. It targets scalable, secure smart contracts and governance.",
            'LINK': "Chainlink (LINK) is a decentralized oracle network that delivers secure off‑chain data (like prices) to smart contracts, enabling DeFi and other use cases.",
            'MATIC': "Polygon (MATIC) is an ecosystem of scaling solutions for Ethereum (PoS chain, zk‑rollups). It aims to reduce fees and increase throughput while inheriting Ethereum security.",
            'BNB': "BNB Chain is a PoS‑style blockchain optimized for throughput and low fees, commonly used for trading and DeFi applications.",
            'LTC': "Litecoin (LTC) is a peer‑to‑peer cryptocurrency inspired by Bitcoin with faster block times and different hashing (Scrypt).",
            'XRP': "XRP is a digital asset used in Ripple’s payment protocols to facilitate fast, low‑cost international transfers on a permissioned validator set.",
            'DOGE': "Dogecoin (DOGE) is a meme‑origin cryptocurrency derived from Litecoin, primarily used for tipping and community‑driven payments.",
            'DOT': "Polkadot (DOT) is a multi‑chain protocol enabling application‑specific parachains to share security and interoperability via the Relay Chain.",
            'UNI': "Uniswap (UNI) governs the Uniswap protocol, an automated market maker (AMM) enabling decentralized token swaps without order books."
        }
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.trained_models_dir = os.path.join(base_dir, '..', '..', 'trained_models')
        self.index_path = index_path or os.path.join(self.trained_models_dir, 'rag_index.index')
        self.data_path = data_path or os.path.join(self.trained_models_dir, 'rag_data.json')

        self.load_index()

    def load_index(self):
        """Loads the FAISS index and RAG data from disk."""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.data_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded index with {self.index.ntotal} vectors")
                return True
            else:
                logger.warning("Index or data file not found, skipping load.")
                return False
        except Exception as e:
            logger.error(f"Error loading FAISS index or data: {e}", exc_info=True)
            self.index = None
            self.data = []
            return False

    def load_crypto_dataset(self, csv_path: str) -> pd.DataFrame:
        """Load cryptocurrency dataset"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded dataset with {len(df)} records from {csv_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better embedding"""
        if pd.isna(text):
            return ""
        
        text = str(text).strip()
        text = re.sub(r'[^\w\s\.\,\!\?\-\$\%]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text

    def create_knowledge_base(self, df: pd.DataFrame) -> List[Dict]:
        """Create knowledge base from cryptocurrency dataset, including definitions"""
        knowledge_base = []
        
        try:
            for _, row in df.iterrows():
                symbol = str(row.get('Symbol', '')).strip()
                name = str(row.get('Name', '')).strip()
                
                if not symbol or symbol == 'nan':
                    continue
                
                basic_info = {
                    'id': f"{symbol}_basic",
                    'text': f"{name} ({symbol}) is a cryptocurrency. Current price: ${row.get('Price (Intraday)', 'N/A')}. Market cap: {row.get('Market Cap', 'N/A')}. Volume: {row.get('Volume in Currency (24Hr)', 'N/A')}.",
                    'metadata': { 'type': 'basic_info', 'symbol': symbol, 'name': name, 'price': row.get('Price (Intraday)', ''), 'market_cap': row.get('Market Cap', ''), 'volume': row.get('Volume in Currency (24Hr)', '') }
                }
                knowledge_base.append(basic_info)

                sym_up = symbol.upper()
                definition_text = self.coin_definitions.get(sym_up) or (f"{name} ({symbol}) is a blockchain project...")
                knowledge_base.append({'id': f"{symbol}_definition", 'text': definition_text, 'metadata': {'type': 'definition', 'symbol': symbol, 'name': name}})
                
                price_change = row.get('% Change', '')
                if price_change and price_change != 'nan':
                    knowledge_base.append({'id': f"{symbol}_change", 'text': f"{name} ({symbol}) has changed by {price_change} in the last 24 hours...", 'metadata': { 'type': 'price_change', 'symbol': symbol, 'name': name, 'change_percent': price_change, 'change_amount': row.get('Change', '') }})
                
                market_cap = row.get('Market Cap', '')
                if market_cap and market_cap != 'nan':
                    knowledge_base.append({'id': f"{symbol}_market_cap", 'text': f"{name} ({symbol}) has a market capitalization of {market_cap}...", 'metadata': {'type': 'market_cap', 'symbol': symbol, 'name': name, 'market_cap': market_cap}})
                
                volume = row.get('Volume in Currency (24Hr)', '')
                if volume and volume != 'nan':
                    knowledge_base.append({'id': f"{symbol}_volume", 'text': f"{name} ({symbol}) has a 24-hour trading volume of {volume}...", 'metadata': {'type': 'volume', 'symbol': symbol, 'name': name, 'volume': volume}})
            
            logger.info(f"Created knowledge base with {len(knowledge_base)} entries")
            return knowledge_base
        
        except Exception as e:
            logger.error(f"Error creating knowledge base: {e}")
            raise

    def _get_market_cap_tier(self, market_cap: str) -> str:
        try:
            numeric_value = float(re.sub(r'[^\d\.]', '', market_cap))
            if 'T' in market_cap.upper(): return "largest"
            if 'B' in market_cap.upper():
                if numeric_value > 50: return "major"
                if numeric_value > 10: return "significant"
                return "moderate"
            return "smaller"
        except:
            return "unknown"
    
    def _get_volume_analysis(self, volume: str) -> str:
        try:
            numeric_value = float(re.sub(r'[^\d\.]', '', volume))
            if 'B' in volume.upper():
                if numeric_value > 5: return "very high"
                if numeric_value > 1: return "high"
                return "moderate"
            if 'M' in volume.upper():
                if numeric_value > 500: return "high"
                if numeric_value > 100: return "moderate"
                return "low"
            return "very low"
        except:
            return "unknown"
            
    def build_index_from_directory(self, directory_path: str):
        try:
            csv_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.csv')]
            if not csv_files:
                raise ValueError("No CSV files found in the specified directory.")
            all_dfs = [self.load_crypto_dataset(csv_file) for csv_file in csv_files]
            df = pd.concat(all_dfs, ignore_index=True)
            df.drop_duplicates(subset=['Symbol'], keep='last', inplace=True)
            self.data = self.create_knowledge_base(df)
            texts = [item['text'] for item in self.data]
            embeddings = self.model.encode(texts)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors from {len(csv_files)} files.")
        except Exception as e:
            logger.error(f"Error building index from directory: {e}")
            raise

    def save_index(self, index_path: str, data_path: str):
        try:
            if self.index is None or self.data is None:
                raise ValueError("No index or data to save")
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            faiss.write_index(self.index, index_path)
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Index saved to {index_path}")
            logger.info(f"Data saved to {data_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        try:
            if self.index is None or not self.data:
                raise ValueError("Index not loaded")
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if 0 <= idx < len(self.data):
                    result = self.data[idx].copy()
                    result['similarity_score'] = float(score)
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            return []

    # --- UPGRADED AND ADDED API FUNCTIONS ---

    def _fallback_llm(self, query: str, context: Optional[List[str]] = None) -> Optional[str]:
        """
        UPGRADED: Tries OpenRouter first for high-quality responses, 
        then falls back to Hugging Face if needed.
        """
        # --- Priority 1: Try OpenRouter ---
        openrouter_key = settings.openrouter_api_key
        if openrouter_key and "your-openrouter-api-key" not in openrouter_key:
            try:
                response = httpx.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistralai/mistral-7b-instruct:free", # Using a free, high-quality model
                        "messages": [
                            {"role": "system", "content": "You are a helpful crypto expert. Answer questions clearly and concisely."},
                            {"role": "user", "content": query}
                        ]
                    },
                    timeout=15.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    logger.warning(f"OpenRouter API failed with status {response.status_code}. Falling back.")
            except Exception as e:
                logger.error(f"OpenRouter API error: {e}. Falling back.")

        # --- Priority 2: Fallback to Hugging Face (Your original _fallback_llm code) ---
        huggingface_key = settings.huggingface_api_key
        if huggingface_key and "your-huggingface-api-key" not in huggingface_key:
            try:
                model = os.getenv('HF_FALLBACK_MODEL', 'mistralai/Mistral-7B-Instruct-v0.3')
                prompt = (
                    "You are a helpful crypto assistant. Answer concisely in 3-6 sentences. "
                    "If the question is off-topic, answer generally without making up facts.\n\n"
                    f"Question: {query}\n"
                )
                if context:
                    prompt += f"Context (optional):\n{', '.join(context[:3])}\n"
                
                prompt += "Answer:"
                
                headers = {"Authorization": f"Bearer {huggingface_key}"}
                payload = {"inputs": prompt, "parameters": {"max_new_tokens": 220, "temperature": 0.6}}
                with httpx.Client(timeout=10.0) as client:
                    r = client.post(f"https://api-inference.huggingface.co/models/{model}", headers=headers, json=payload)
                    if r.status_code == 200:
                        data = r.json()
                        full_text = data[0]['generated_text'] if isinstance(data, list) and data else data.get('generated_text', '')
                        return full_text.split("Answer:")[-1].strip()
            except Exception as e:
                logger.error(f"Hugging Face API error: {e}")
        
        logger.warning("No valid LLM API key (OpenRouter or Hugging Face) is configured.")
        return None

    def _get_latest_news(self, crypto_name: str) -> Optional[str]:
        """Fetches the latest news headlines using News API."""
        api_key = settings.news_api_key
        if not api_key or "your-newsapi-key" in api_key:
            return "News functionality is currently unavailable."
        
        try:
            url = f"https://newsapi.org/v2/everything?q={crypto_name}&apiKey={api_key}&language=en&sortBy=publishedAt&pageSize=3"
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    articles = response.json().get('articles', [])
                    if articles:
                        headlines = [f"- {article['title']}" for article in articles]
                        return "Here are the latest headlines:\n" + "\n".join(headlines)
                    return f"I couldn't find any recent news for {crypto_name}."
                return "Sorry, I was unable to fetch the latest news at the moment."
        except Exception as e:
            logger.error(f"News API error: {e}")
            return "An error occurred while fetching news."

    def _get_coinmarketcap_data(self, symbol: str) -> Optional[str]:
        """Fetches detailed coin information from CoinMarketCap API."""
        api_key = settings.coinmarketcap_api_key
        if not api_key or "your-coinmarketcap-api-key" in api_key:
            return "Detailed coin information is currently unavailable."
            
        try:
            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
            headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}
            params = {'symbol': symbol.upper()}
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json().get('data', {}).get(symbol.upper(), {})
                    if not data or 'urls' not in data:
                        return f"I couldn't find detailed information for {symbol} on CoinMarketCap."
                    
                    urls = data.get('urls', {})
                    response_parts = [f"Here are some details for {data.get('name', symbol)}:"]
                    if urls.get('website'): response_parts.append(f"- **Website**: {urls['website'][0]}")
                    if urls.get('technical_doc'): response_parts.append(f"- **Whitepaper**: {urls['technical_doc'][0]}")
                    if urls.get('twitter'): response_parts.append(f"- **Twitter**: {urls['twitter'][0]}")
                    if urls.get('reddit'): response_parts.append(f"- **Reddit**: {urls['reddit'][0]}")
                    return "\n".join(response_parts)
                return "Sorry, I was unable to fetch coin details."
        except Exception as e:
            logger.error(f"CoinMarketCap API error: {e}")
            return "An error occurred while fetching coin details."

    # --- YOUR ORIGINAL generate_response FUNCTION WITH THE SMART ROUTER ADDED ---
    def generate_response(self, query: str, context_limit: int = 5) -> Dict:
        try:
            ql = query.lower()

            # --- SMART ROUTER LOGIC ---
            definitional_keywords = ['what is', 'what are', 'explain', 'define', 'how do', 'compare']
            if any(keyword in ql for keyword in definitional_keywords):
                llm_response = self._fallback_llm(query)
                if llm_response:
                    return {'response': llm_response, 'confidence': 0.9, 'sources': []}

            def extract_crypto_entity(q):
                words = q.replace('news', '').replace('about', '').replace('for', '').replace('details', '').replace('website', '').replace('whitepaper', '').strip().split()
                return words[-1] if words else None
            
            crypto_entity = extract_crypto_entity(ql)

            if 'news' in ql or 'latest' in ql:
                if crypto_entity:
                    return {'response': self._get_latest_news(crypto_entity), 'confidence': 0.95, 'sources': []}
                else:
                    return {'response': "Please specify which cryptocurrency you want news for.", 'confidence': 0.9, 'sources': []}

            if 'details' in ql or 'website' in ql or 'whitepaper' in ql:
                if crypto_entity:
                    return {'response': self._get_coinmarketcap_data(crypto_entity), 'confidence': 0.95, 'sources': []}
                else:
                    return {'response': "Please specify which cryptocurrency you want details for.", 'confidence': 0.9, 'sources': []}

            # --- ORIGINAL RAG LOGIC ---
            search_results = self.search(query, top_k=context_limit)
            
            if not search_results:
                llm = self._fallback_llm(query)
                return {'response': llm or "I don't have specific information about that.", 'confidence': 0.5, 'sources': []}

            is_definition = any(w in ql for w in ['what is', 'explain', 'define', 'overview'])
            is_price = any(w in ql for w in ['price', 'cost', 'value', 'worth'])
            ordered = sorted(search_results, key=lambda r: (0 if r.get('metadata', {}).get('type') == 'definition' and is_definition else 1, -r.get('similarity_score', 0)))
            context = [r['text'] for r in ordered[:context_limit]]
            sources = ordered[:context_limit]
            avg_confidence = sum(r['similarity_score'] for r in search_results) / len(search_results) if search_results else 0
            
            response = self._generate_contextual_response(query, context)
            
            coin_symbol = self._extract_symbol_from_context(sources)
            coin_name = self._extract_name_from_context(sources)
            
            if is_definition and not any(kw in ql for kw in definitional_keywords):
                core_def = (self.coin_definitions.get(coin_symbol) or self.coin_definitions.get(coin_name.upper() if coin_name else None))
                if core_def:
                    response = core_def

            live_section = None
            if coin_symbol and (is_price or 'today' in ql or 'now' in ql):
                live = self._get_live_price_safe(coin_symbol)
                if live:
                    live_section = f"Live: {coin_symbol} price ${live.get('price','?')} • 24h {live.get('change','?')} • MC {live.get('market_cap','?')}"

            if not is_price:
                response = re.sub(r"Current price:[^\.]*\.\s*", "", response, flags=re.IGNORECASE)
                response = re.sub(r"Market cap:[^\.]*\.\s*", "", response, flags=re.IGNORECASE)
                response = re.sub(r"Volume:[^\.]*\.\s*", "", response, flags=re.IGNORECASE)
            
            if live_section:
                response += "\n" + live_section

            if avg_confidence < 0.25:
                llm = self._fallback_llm(query, context)
                if llm:
                    return {'response': llm, 'confidence': float(avg_confidence), 'sources': sources}

            return {'response': response, 'confidence': float(avg_confidence), 'sources': sources}

        except Exception as e:
            logger.error(f"Response generation error: {e}", exc_info=True)
            return {'response': "I'm sorry, an error occurred.", 'confidence': 0.0, 'sources': []}

    # --- ALL OF YOUR ORIGINAL HELPER FUNCTIONS ARE PRESERVED HERE ---
    def _generate_contextual_response(self, query: str, context: List[str]) -> str:
        query_lower = query.lower()
        if any(word in query_lower for word in ['price', 'cost', 'value', 'worth']): return self._generate_price_response(query, context)
        elif any(word in query_lower for word in ['market cap', 'market capitalization']): return self._generate_market_cap_response(query, context)
        elif any(word in query_lower for word in ['volume', 'trading', 'activity']): return self._generate_volume_response(query, context)
        elif any(word in query_lower for word in ['change', 'performance']): return self._generate_change_response(query, context)
        else: return self._generate_general_response(query, context)

    def _generate_price_response(self, query: str, context: List[str]) -> str:
        response_parts = [ctx for ctx in context if 'price' in ctx.lower()]
        return " ".join(response_parts[:2]) if response_parts else "I don't have current price information for that."

    def _generate_market_cap_response(self, query: str, context: List[str]) -> str:
        response_parts = [ctx for ctx in context if 'market cap' in ctx.lower()]
        return " ".join(response_parts[:2]) if response_parts else "I don't have market cap information for that."

    def _generate_volume_response(self, query: str, context: List[str]) -> str:
        response_parts = [ctx for ctx in context if 'volume' in ctx.lower()]
        return " ".join(response_parts[:2]) if response_parts else "I don't have trading volume information for that."

    def _generate_change_response(self, query: str, context: List[str]) -> str:
        response_parts = [ctx for ctx in context if 'change' in ctx.lower()]
        return " ".join(response_parts[:2]) if response_parts else "I don't have price change information for that."

    def _generate_general_response(self, query: str, context: List[str]) -> str:
        return context[0] if context else "I don't have specific information about that."

    def _extract_symbol_from_context(self, sources: List[Dict]) -> Optional[str]:
        try:
            for s in sources:
                sym = s.get('metadata', {}).get('symbol')
                if sym: return str(sym).upper()
        except: pass
        return None

    def _extract_name_from_context(self, sources: List[Dict]) -> Optional[str]:
        try:
            for s in sources:
                nm = s.get('metadata', {}).get('name')
                if nm: return str(nm)
        except: pass
        return None

    def _get_live_price_safe(self, symbol: str) -> Optional[Dict]:
        try:
            mapping = { 'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'ADA': 'cardano', 'LINK': 'chainlink', 'LTC': 'litecoin', 'XRP': 'ripple', 'DOGE': 'dogecoin', 'DOT': 'polkadot', 'UNI': 'uniswap', 'BNB': 'binancecoin', 'MATIC': 'matic-network'}
            coin_id = mapping.get(symbol.upper())
            if not coin_id: return None
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
            r = requests.get(url, timeout=4)
            if r.status_code != 200: return None
            data = r.json().get(coin_id)
            if not data: return None
            return {
                'price': round(float(data.get('usd', 0)), 4),
                'change': f"{round(float(data.get('usd_24h_change', 0)), 2)}%",
                'market_cap': f"${data.get('usd_market_cap', 'N/A'):,}"
            }
        except Exception:
            return None

    def get_supported_cryptocurrencies(self) -> List[str]:
        if not self.data: return []
        symbols = set()
        for item in self.data:
            metadata = item.get('metadata', {})
            symbol = metadata.get('symbol')
            if symbol: symbols.add(symbol)
        return sorted(list(symbols))

    def get_model_info(self) -> Dict:
        return {
            'model_name': self.model_name,
            'index_size': self.index.ntotal if self.index else 0,
            'data_size': len(self.data) if self.data else 0,
            'supported_cryptocurrencies': len(self.get_supported_cryptocurrencies())
        }

# Global chatbot instance
chatbot = None

def get_chatbot() -> CryptoRAGChatbot:
    global chatbot
    if chatbot is None:
        chatbot = CryptoRAGChatbot()
    return chatbot