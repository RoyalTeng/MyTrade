"""
投资组合管理器

管理投资组合的现金、持仓、交易记录等状态。
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

import pandas as pd
from pydantic import BaseModel


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    shares: int = 0
    avg_cost: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    
    def update_market_value(self, current_price: float) -> None:
        """更新市值和未实现盈亏"""
        if self.shares > 0:
            self.market_value = self.shares * current_price
            self.unrealized_pnl = self.market_value - (self.shares * self.avg_cost)
        else:
            self.market_value = 0.0
            self.unrealized_pnl = 0.0


@dataclass  
class TradeRecord:
    """交易记录"""
    timestamp: str
    symbol: str
    action: str  # BUY, SELL
    shares: int
    price: float
    commission: float
    total_amount: float
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'action': self.action,
            'shares': self.shares,
            'price': self.price,
            'commission': self.commission,
            'total_amount': self.total_amount,
            'reason': self.reason
        }


class PortfolioManager:
    """
    投资组合管理器
    
    功能：
    - 管理现金和持仓
    - 执行买卖交易
    - 计算收益和绩效指标
    - 记录交易历史
    """
    
    def __init__(
        self, 
        initial_cash: float = 1000000.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005
    ):
        """
        初始化投资组合管理器
        
        Args:
            initial_cash: 初始现金
            commission_rate: 佣金费率
            slippage_rate: 滑点费率
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        # 持仓管理
        self.positions: Dict[str, Position] = {}
        
        # 交易记录
        self.trade_history: List[TradeRecord] = []
        
        # 每日净值记录
        self.daily_values: List[Dict[str, Any]] = []
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.logger.info(f"PortfolioManager initialized with ${initial_cash:,.2f}")
    
    def execute_trade(
        self, 
        symbol: str,
        action: str,
        shares: int,
        price: float,
        timestamp: str = None,
        reason: str = ""
    ) -> bool:
        """
        执行交易
        
        Args:
            symbol: 股票代码
            action: 交易动作 (BUY/SELL)
            shares: 股数
            price: 价格
            timestamp: 时间戳
            reason: 交易原因
        
        Returns:
            是否执行成功
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        if shares <= 0:
            self.logger.warning(f"Invalid shares: {shares}")
            return False
        
        # 考虑滑点
        if action == "BUY":
            execution_price = price * (1 + self.slippage_rate)
        else:
            execution_price = price * (1 - self.slippage_rate)
        
        # 计算交易金额和手续费
        trade_amount = shares * execution_price
        commission = trade_amount * self.commission_rate
        total_cost = trade_amount + commission
        
        try:
            if action == "BUY":
                return self._execute_buy(symbol, shares, execution_price, commission, total_cost, timestamp, reason)
            elif action == "SELL":
                return self._execute_sell(symbol, shares, execution_price, commission, total_cost, timestamp, reason)
            else:
                self.logger.error(f"Invalid action: {action}")
                return False
                
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
            return False
    
    def _execute_buy(
        self, 
        symbol: str, 
        shares: int, 
        price: float, 
        commission: float, 
        total_cost: float,
        timestamp: str,
        reason: str
    ) -> bool:
        """执行买入"""
        # 检查现金是否充足
        if self.cash < total_cost:
            self.logger.warning(f"Insufficient cash: need ${total_cost:,.2f}, have ${self.cash:,.2f}")
            return False
        
        # 更新现金
        self.cash -= total_cost
        
        # 更新持仓
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        
        position = self.positions[symbol]
        
        # 计算新的平均成本
        total_shares = position.shares + shares
        total_cost_basis = (position.shares * position.avg_cost) + (shares * price)
        new_avg_cost = total_cost_basis / total_shares if total_shares > 0 else price
        
        position.shares = total_shares
        position.avg_cost = new_avg_cost
        
        # 记录交易
        trade = TradeRecord(
            timestamp=timestamp,
            symbol=symbol,
            action="BUY",
            shares=shares,
            price=price,
            commission=commission,
            total_amount=total_cost,
            reason=reason
        )
        self.trade_history.append(trade)
        
        self.logger.info(f"BUY executed: {shares} shares of {symbol} at ${price:.2f}")
        return True
    
    def _execute_sell(
        self, 
        symbol: str, 
        shares: int, 
        price: float, 
        commission: float, 
        total_cost: float,
        timestamp: str,
        reason: str
    ) -> bool:
        """执行卖出"""
        # 检查持仓是否充足
        if symbol not in self.positions:
            self.logger.warning(f"No position in {symbol}")
            return False
        
        position = self.positions[symbol]
        if position.shares < shares:
            self.logger.warning(f"Insufficient shares: need {shares}, have {position.shares}")
            return False
        
        # 计算实际收入
        trade_amount = shares * price
        net_proceeds = trade_amount - commission
        
        # 更新现金
        self.cash += net_proceeds
        
        # 更新持仓
        position.shares -= shares
        
        # 如果持仓为0，清除平均成本
        if position.shares == 0:
            position.avg_cost = 0.0
        
        # 记录交易
        trade = TradeRecord(
            timestamp=timestamp,
            symbol=symbol,
            action="SELL",
            shares=shares,
            price=price,
            commission=commission,
            total_amount=-net_proceeds,  # 负数表示现金流入
            reason=reason
        )
        self.trade_history.append(trade)
        
        self.logger.info(f"SELL executed: {shares} shares of {symbol} at ${price:.2f}")
        return True
    
    def update_market_values(self, price_data: Dict[str, float], timestamp: str = None) -> None:
        """
        更新所有持仓的市值
        
        Args:
            price_data: {symbol: current_price} 映射
            timestamp: 时间戳
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        total_market_value = 0.0
        
        for symbol, position in self.positions.items():
            if symbol in price_data:
                current_price = price_data[symbol]
                position.update_market_value(current_price)
                total_market_value += position.market_value
        
        # 记录每日净值
        total_value = self.cash + total_market_value
        daily_record = {
            'timestamp': timestamp,
            'cash': self.cash,
            'market_value': total_market_value,
            'total_value': total_value,
            'total_return': (total_value - self.initial_cash) / self.initial_cash,
            'positions': {symbol: {
                'shares': pos.shares,
                'market_value': pos.market_value,
                'unrealized_pnl': pos.unrealized_pnl
            } for symbol, pos in self.positions.items() if pos.shares > 0}
        }
        
        self.daily_values.append(daily_record)
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """获取投资组合摘要"""
        total_market_value = sum(pos.market_value for pos in self.positions.values())
        total_value = self.cash + total_market_value
        total_return = (total_value - self.initial_cash) / self.initial_cash
        
        # 计算已实现盈亏（从交易记录）
        realized_pnl = 0.0
        for trade in self.trade_history:
            if trade.action == "SELL":
                # 简化计算，实际应该考虑FIFO等方法
                realized_pnl += trade.total_amount
        
        # 计算未实现盈亏
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        
        return {
            'initial_cash': self.initial_cash,
            'current_cash': self.cash,
            'market_value': total_market_value,
            'total_value': total_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'num_positions': len([p for p in self.positions.values() if p.shares > 0]),
            'num_trades': len(self.trade_history)
        }
    
    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """获取所有持仓信息"""
        return {
            symbol: {
                'shares': pos.shares,
                'avg_cost': pos.avg_cost,
                'market_value': pos.market_value,
                'unrealized_pnl': pos.unrealized_pnl,
                'unrealized_pnl_pct': pos.unrealized_pnl / (pos.shares * pos.avg_cost) * 100 if pos.shares > 0 and pos.avg_cost > 0 else 0.0
            }
            for symbol, pos in self.positions.items() 
            if pos.shares > 0
        }
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """获取交易历史"""
        return [trade.to_dict() for trade in self.trade_history]
    
    def get_daily_values(self) -> pd.DataFrame:
        """获取每日净值DataFrame"""
        if not self.daily_values:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.daily_values)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    
    def calculate_performance_metrics(self) -> Dict[str, float]:
        """计算绩效指标"""
        if not self.daily_values:
            return {}
        
        df = self.get_daily_values()
        
        if len(df) < 2:
            return {}
        
        # 计算日收益率
        df['daily_return'] = df['total_value'].pct_change().fillna(0)
        
        # 计算绩效指标
        total_return = (df['total_value'].iloc[-1] - self.initial_cash) / self.initial_cash
        
        # 年化收益率（假设252个交易日）
        trading_days = len(df)
        annual_return = (1 + total_return) ** (252 / max(trading_days, 1)) - 1
        
        # 波动率
        volatility = df['daily_return'].std() * (252 ** 0.5)
        
        # 夏普比率（假设无风险利率为3%）
        risk_free_rate = 0.03
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 最大回撤
        rolling_max = df['total_value'].expanding().max()
        drawdown = (df['total_value'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # 胜率
        win_rate = (df['daily_return'] > 0).sum() / len(df) if len(df) > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'trading_days': trading_days
        }
    
    def reset(self) -> None:
        """重置投资组合"""
        self.cash = self.initial_cash
        self.positions.clear()
        self.trade_history.clear()
        self.daily_values.clear()
        
        self.logger.info("Portfolio reset")