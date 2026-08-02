import math

#===stock evaluation==========
def graham_value(eps, bvps):
    """Calculates Graham Multiple Intrinsic Value: GM = sqrt(22.5 * EPS * BVPS)"""
    if eps <= 0 or bvps <= 0:
        return None
    return math.sqrt(22.5 * eps * bvps)

def margin_of_safety(intrinsic_value, current_price):
    """Calculates percentage discount of market price relative to intrinsic value."""
    if not intrinsic_value or intrinsic_value <= 0:
        return None
    return (intrinsic_value - current_price) / intrinsic_value

def peg_ratio(pe_ratio, earnings_growth):
    """PEG Ratio = (P/E) / Earnings Growth Rate"""
    if earnings_growth <= 0:
        return None
    return pe_ratio / earnings_growth

def return_on_equity(net_income, shareholders_equity):
    """ROE = (Net Income / Shareholders Equity) * 100"""
    if shareholders_equity <= 0:
        return None
    return (net_income / shareholders_equity) * 100

def net_current_assets(current_assets, current_liabilities):
    return current_assets - current_liabilities
#===============================

#===ratio calculations======
def liquidity_ratio(current_assets, current_liabilities):
    if current_liabilities <= 0:
        return None
    return current_assets / current_liabilities

def solvency_ratio(total_debt, shareholders_equity):
    if shareholders_equity <= 0:
        return None
    return total_debt / shareholders_equity

def profit_ratio(current_profit, net_sales):
    if net_sales <= 0:
        return None
    return current_profit / net_sales
#=================