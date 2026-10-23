import React from 'react';

// Sample array of data objects
const employees = [
  { id: 1, name: 'Alice Johnson', role: 'Software Engineer', department: 'Engineering' },
  { id: 2, name: 'Bob Smith', role: 'UI/UX Designer', department: 'Design' },
  { id: 3, name: 'Charlie Brown', role: 'Product Manager', department: 'Product' },
  { id: 4, name: 'Dana White', role: 'Data Analyst', department: 'Analytics' }
];

export default function DataTable() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Employee Directory</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
        <thead>
          <tr style={{ backgroundColor: '#f2f2f2', textAlign: 'left' }}>
            <th style={cellStyle}>ID</th>
            <th style={cellStyle}>Name</th>
            <th style={cellStyle}>Role</th>
            <th style={cellStyle}>Department</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((employee) => (
            <tr key={employee.id} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={cellStyle}>{employee.id}</td>
              <td style={cellStyle}>{employee.name}</td>
              <td style={cellStyle}>{employee.role}</td>
              <td style={cellStyle}>{employee.department}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Simple inline styling object for cells
const cellStyle = {
  padding: '12px',
  border: '1px solid #ddd'
};



print("\n")
print("-----------------Daily Market Metrics-------------------")
print(f"Nasdaq WTD: {weekly_performance['^IXIC'] * 100:.2f}%")
print(f"Nasdaq Closing Price: {nasdaq_price_yd:.2f}, Nasdaq Performance YD: {nasdaq_perf_yd * 100:.2f}%")
print("\n")
#print(f"Nasdaq YTD Drawdown: {mdd['^IXIC'] * 100:.2f}%")
print(f"S&P 500 WTD: {weekly_performance['^GSPC'] * 100:.2f}%")
print(f"S&P 500 Closing Price: {sp500_price_yd:.2f}, S&P 500 Performance YD: {sp500_perf_yd * 100:.2f}%")
print("\n")
#print(f"S&P 500 YTD Drawdown: {mdd['^GSPC'] * 100:.2f}%")
print(f"Dow WTD: {weekly_performance['^DJI'] * 100:.2f}%")
print(f"Dow Closing Price: {dow_price_yd:.2f}, Dow Performance YD: {dow_perf_yd * 100:.2f}%")
print("\n")
#print(f"Dow YTD Drawdown: {mdd['^DJI'] * 100:.2f}%")
print(f"10-Year Yield From Yesterday: {ten_year_yield['^TNX']:.3f}%")
print("\n")



def calculate_index_metrics(rets):
    rets_lastweek = rets.iloc[-5:]
    weekly_performance = np.prod(1 + rets_lastweek) - 1
    return weekly_performance

def max_drawdown(wealth_index):
  previous_peaks = wealth_index.cummax() 
  drawdown = (wealth_index - previous_peaks) / previous_peaks 
  mdd = drawdown.min()
  return mdd

def get_metrics() -> dict:
    weekly_performance = calculate_index_metrics(rets)
    #ten_year_yield = yf.download(['^TNX'], interval='1d', start='2026-01-01', auto_adjust=True)['Close']
    #ten_year_yield = ten_year_yield.iloc[-2]
    #nasdaq_price_yd = prices['^IXIC'].iloc[-2]
    #nasdaq_perf_yd = (nasdaq_price_yd / prices['^IXIC'].iloc[-3]) - 1
    #nasdaq_perf_ytd = (nasdaq_price_yd / prices['^IXIC'].iloc[0]) - 1
    #sp500_price_yd = prices['^GSPC'].iloc[-2]
    #sp500_perf_yd = (sp500_price_yd / prices['^GSPC'].iloc[-3]) - 1
    #sp500_perf_ytd = (sp500_price_yd / prices['^GSPC'].iloc[0]) - 1
    #dow_price_yd = prices['^DJI'].iloc[-2]
    #dow_perf_yd = (dow_price_yd / prices['^DJI'].iloc[-3]) - 1
    #dow_perf_ytd = (dow_price_yd / prices['^DJI'].iloc[0]) - 1
    #last_hyspread = hyspread.iloc[-1]
    #last_ten_two_year_yield = ten_two_year_yield_fred.iloc[-1]
    return {
        "Nasdaq WTD": round(float(weekly_performance['^IXIC'] * 100), 2),
        "Nasdaq Closing Price": round(float(nasdaq_price_yd), 2),
        "Nasdaq Performance YD": round(float(nasdaq_perf_yd * 100), 2),
        "Nasdaq Performance YTD": round(float(nasdaq_perf_ytd * 100), 2),

        "S&P 500 WTD": round(float(weekly_performance['^GSPC'] * 100), 2),
        "S&P 500 Closing Price": round(float(sp500_price_yd), 2),
        "S&P 500 Performance YD": round(float(sp500_perf_yd * 100), 2),
        "S&P 500 Performance YTD": round(float(sp500_perf_ytd * 100), 2),

        "Dow WTD": round(float(weekly_performance['^DJI'] * 100), 2),
        "Dow Closing Price": round(float(dow_price_yd), 2),
        "Dow Performance YD": round(float(dow_perf_yd * 100), 2),
        "Dow Performance YTD": round(float(dow_perf_ytd * 100), 2),

        "10-Year Yield (%)": round(float(ten_year_yield), 3),
        "Last High Yield Option-Adjusted Spread (bps)": round(float(last_hyspread * 100), 3),
        "Last 10Y2Y Yield (bps)": round(float(last_ten_two_year_yield * 100), 3)
    }