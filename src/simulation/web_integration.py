"""
Simulation Trading System - Web Interface Integration Example

Shows how to integrate simulation trading features in portfolio_app.py
"""

# Add to portfolio_app.py imports section
from src.simulation.account_manager import SimulationAccountManager
from src.simulation.trader import VirtualTrader
from src.simulation.backtest_engine import BacktestEngine
from src.simulation.models import TransactionType, OrderType

# Add simulation trading manager initialization at the beginning of main function
simulation_manager = SimulationAccountManager()
virtual_trader = VirtualTrader(simulation_manager)
backtest_engine = BacktestEngine()

# Add simulation trading option to sidebar
def add_simulation_sidebar():
    """Add simulation trading sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎮 Simulation Trading")

    simulation_page = st.sidebar.selectbox(
        "Simulation Trading Features",
        ["Account Management", "Virtual Trading", "Historical Backtesting", "Performance Analysis"],
        key="simulation_page"
    )

    return simulation_page

# Account management page
def show_simulation_accounts():
    """Display simulation account management page"""
    st.header("🎮 Simulation Trading Accounts")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("My Accounts")

        # Get user accounts (assuming user_id from session)
        user_id = "demo_user"  # Temporary user ID
        accounts = simulation_manager.get_user_accounts(user_id)

        if not accounts:
            st.info("You don't have any simulation accounts yet. Create one to start investing!")
            if st.button("Create Simulation Account", type="primary"):
                account = simulation_manager.create_account(
                    user_id=user_id,
                    account_name="My First Simulation Account",
                    initial_balance=100000.0
                )
                st.success(f"✅ Account created successfully! Initial balance: ${account.initial_balance:,.0f}")
                st.rerun()
        else:
            for account in accounts:
                with st.expander(f"📊 {account.account_name}", expanded=True):
                    col_a, col_b, col_c = st.columns(3)

                    with col_a:
                        st.metric("Total Assets", f"${account.total_value:,.0f}")
                        st.metric("Available Funds", f"${account.available_balance:,.0f}")

                    with col_b:
                        pnl = account.total_value - account.initial_balance
                        pnl_pct = account.total_return
                        st.metric("P&L", f"${pnl:+,.0f}",
                                delta=f"{pnl_pct:+.1f}%" if pnl_pct else None)

                    with col_c:
                        positions = simulation_manager.calculate_positions(account.account_id)
                        st.metric("Position Stocks", len(positions))
                        st.metric("Total Return", f"{account.total_return:+.1f}%")

    with col2:
        st.subheader("Quick Actions")

        if st.button("💰 Add Funds", type="secondary"):
            # Add deposit dialog here
            pass

        if st.button("📈 View Transaction History", type="secondary"):
            # Navigate to transaction history page here
            pass

# Virtual trading page
def show_virtual_trading():
    """Display virtual trading page"""
    st.header("💹 Virtual Trading")

    # Select account
    user_id = "demo_user"
    accounts = simulation_manager.get_user_accounts(user_id)

    if not accounts:
        st.warning("Please create a simulation account first")
        return

    account_id = st.selectbox(
        "Select Trading Account",
        [acc.account_id for acc in accounts],
        format_func=lambda x: next(acc.account_name for acc in accounts if acc.account_id == x)
    )

    account = next(acc for acc in accounts if acc.account_id == account_id)

    # Display account status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Available Funds", f"${account.available_balance:,.0f}")
    with col2:
        st.metric("Total Assets", f"${account.total_value:,.0f}")
    with col3:
        st.metric("Return Rate", f"{account.total_return:+.1f}%")

    st.markdown("---")

    # Trading form
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Buy Stocks")
        with st.form("buy_form"):
            buy_symbol = st.text_input("Stock Symbol", "AAPL").upper()
            buy_quantity = st.number_input("Quantity", min_value=1, value=10)

            buy_submitted = st.form_submit_button("Buy", type="primary")

            if buy_submitted:
                try:
                    # Validate order
                    validation = virtual_trader.validate_order(
                        account_id, buy_symbol, buy_quantity, TransactionType.BUY
                    )

                    if validation["valid"]:
                        # Execute trade
                        transaction = virtual_trader.execute_buy_order(
                            account_id, buy_symbol, buy_quantity
                        )

                        st.success(f"✅ Buy successful!\\n"
                                 f"Stock: {buy_symbol}\\n"
                                 f"Quantity: {buy_quantity}\\n"
                                 f"Price: ${transaction.price:.2f}\\n"
                                 f"Total Amount: ${transaction.total_amount:.2f}")

                        st.rerun()
                    else:
                        st.error(f"❌ Trade failed: {validation['message']}")

                except Exception as e:
                    st.error(f"❌ Trade failed: {str(e)}")

    with col2:
        st.subheader("📉 Sell Stocks")
        with st.form("sell_form"):
            # Get current positions
            positions = simulation_manager.calculate_positions(account_id)
            if positions:
                sell_symbol = st.selectbox("Select Stock", list(positions.keys()))
                max_quantity = positions[sell_symbol].quantity
                sell_quantity = st.number_input("Quantity", min_value=1, max_value=max_quantity, value=min(10, max_quantity))

                sell_submitted = st.form_submit_button("Sell", type="secondary")

                if sell_submitted:
                    try:
                        # Validate order
                        validation = virtual_trader.validate_order(
                            account_id, sell_symbol, sell_quantity, TransactionType.SELL
                        )

                        if validation["valid"]:
                            # Execute trade
                            transaction = virtual_trader.execute_sell_order(
                                account_id, sell_symbol, sell_quantity
                            )

                            st.success(f"✅ Sell successful!\\n"
                                     f"Stock: {sell_symbol}\\n"
                                     f"Quantity: {sell_quantity}\\n"
                                     f"Price: ${transaction.price:.2f}\\n"
                                     f"Total Amount: ${transaction.total_amount:.2f}")

                            st.rerun()
                        else:
                            st.error(f"❌ Trade failed: {validation['message']}")

                    except Exception as e:
                        st.error(f"❌ Trade failed: {str(e)}")
            else:
                st.info("No positions available")

    # Display current positions
    st.markdown("---")
    st.subheader("📊 Current Positions")

    positions = simulation_manager.calculate_positions(account_id)
    if positions:
        positions_data = []
        for symbol, position in positions.items():
            positions_data.append({
                "Stock": symbol,
                "Quantity": position.quantity,
                "Average Cost": f"${position.average_cost:.2f}",
                "Current Price": f"${position.current_price:.2f}",
                "Market Value": f"${position.market_value:.2f}",
                "P&L": f"${position.unrealized_pnl:+.2f}",
                "P&L %": f"{position.unrealized_pnl_pct:+.1f}%"
            })

        st.dataframe(positions_data, use_container_width=True)
    else:
        st.info("No positions")

# Historical backtesting page
def show_backtesting():
    """Display historical backtesting page"""
    st.header("📈 Historical Backtesting")

    with st.form("backtest_form"):
        st.subheader("Backtest Settings")

        col1, col2 = st.columns(2)

        with col1:
            symbols = st.multiselect(
                "Select Stocks",
                ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
                default=["AAPL", "MSFT"]
            )

            strategy = st.selectbox(
                "Investment Strategy",
                ["buy_and_hold", "mean_reversion"],
                format_func=lambda x: {
                    "buy_and_hold": "Buy and Hold",
                    "mean_reversion": "Mean Reversion"
                }.get(x, x)
            )

        with col2:
            start_date = st.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
            end_date = st.date_input("End Date", value=pd.to_datetime("2023-12-31"))
            initial_balance = st.number_input("Initial Balance", min_value=1000, value=100000)

        submitted = st.form_submit_button("Start Backtest", type="primary")

        if submitted and symbols:
            with st.spinner("Running historical backtest..."):
                try:
                    result = backtest_engine.run_backtest(
                        strategy_config={"type": strategy},
                        symbols=symbols,
                        start_date=pd.to_datetime(start_date),
                        end_date=pd.to_datetime(end_date),
                        initial_balance=initial_balance
                    )

                    if result.get("success"):
                        st.success("✅ Backtest completed!")

                        # Display results
                        perf = result["performance"]

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Total Return", f"{perf['total_return']:+.1f}%")
                        with col2:
                            st.metric("Annualized Return", f"{perf['annualized_return']:+.1f}%")
                        with col3:
                            st.metric("Max Drawdown", f"{perf['max_drawdown']:.1f}%")
                        with col4:
                            st.metric("Sharpe Ratio", f"{perf['sharpe_ratio']:.2f}")

                        # Display portfolio value curve
                        portfolio_values = result["portfolio_values"]
                        if portfolio_values:
                            chart_data = pd.DataFrame(portfolio_values)
                            chart_data["date"] = pd.to_datetime(chart_data["date"])

                            st.subheader("📊 Portfolio Value Curve")
                            st.line_chart(chart_data.set_index("date")["value"])

                        # Display transaction records
                        transactions = result["transactions"]
                        if transactions:
                            st.subheader("📋 Transaction Records")
                            txn_df = pd.DataFrame(transactions)
                            txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])
                            st.dataframe(txn_df, use_container_width=True)

                    else:
                        st.error(f"❌ Backtest failed: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")

# Integrate in main function
def integrate_simulation_features():
    """Integrate simulation trading features"""
    simulation_page = add_simulation_sidebar()

    if simulation_page == "Account Management":
        show_simulation_accounts()
    elif simulation_page == "Virtual Trading":
        show_virtual_trading()
    elif simulation_page == "Historical Backtesting":
        show_backtesting()
    elif simulation_page == "Performance Analysis":
        st.header("📊 Performance Analysis")
        st.info("Performance analysis feature is under development...")

# Call in main function
# integrate_simulation_features()
print("Simulation trading system web interface integration code generated")
print("Integrate the above code into portfolio_app.py to enable simulation trading features")