import axios from 'axios';

export function getRiskValue() {
  return axios.get('/api/risk-value');
}
export default getRiskValue;
