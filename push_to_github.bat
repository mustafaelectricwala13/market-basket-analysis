@echo off
echo ==============================================================
echo  Pushing Market Basket Analysis to GitHub...
echo ==============================================================
echo.
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Project successfully pushed to GitHub!
    echo Visit: https://github.com/mustafaelectricwala13/market-basket-analysis
) else (
    echo [FAILED] Please make sure you have created the empty repository
    echo 'market-basket-analysis' on https://github.com/new first!
)
pause
