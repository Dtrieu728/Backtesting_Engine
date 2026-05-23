import axios from 'axios';

const BASE = 'http://localhost:8000/api';

export const getSymbols = () => axios.get(`${BASE}/symbols`);
export const getStrategies = () => axios.get(`${BASE}/strategies`);
export const runBacktest = (config) => axios.post(`${BASE}/backtest`, config);
export const getBacktestResult = (runId) => axios.get(`${BASE}/backtest/${runId}`);