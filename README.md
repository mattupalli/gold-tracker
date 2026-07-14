# Gold Price Tracker - Hyderabad, India

A simple, minimalistic website to track gold prices in Hyderabad, India. No ads, no clutter - just clean price data with historical trends.

## Features

- **Live Prices**: Current 24K, 22K, and 18K gold rates
- **Price by Weight**: Quick reference for 1g, 8g, 10g, and 100g
- **Historical Trends**: Interactive chart with 10/30/90 day views
- **Auto-Updates**: Prices refresh every 4 hours via GitHub Actions
- **Mobile-Friendly**: Works great on phones and tablets
- **No Ads**: Clean, distraction-free experience

## Demo

Visit: `https://yourusername.github.io/gold-tracker`

## Quick Start

### Option 1: GitHub Pages (Recommended)

1. **Fork this repository**
   - Click the "Fork" button at the top right

2. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Select "Deploy from a branch"
   - Choose "main" branch
   - Click Save

3. **Wait for first data fetch**
   - GitHub Actions will run automatically
   - First prices appear within 1-2 hours

4. **Access your site**
   - URL: `https://yourusername.github.io/gold-tracker`

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/gold-tracker.git
cd gold-tracker

# Install Python dependencies
pip install -r scripts/requirements.txt

# Fetch initial price data
python scripts/fetch_prices.py

# Open index.html in your browser
open index.html
```

## Project Structure

```
gold-tracker/
├── .github/workflows/
│   └── update-prices.yml    # Auto-update workflow
├── scripts/
│   ├── fetch_prices.py      # Data fetching script
│   └── requirements.txt     # Python dependencies
├── data/
│   └── prices.json          # Price data (auto-generated)
├── index.html               # Main website
├── style.css                # Styling
├── app.js                   # Interactive features
└── README.md                # This file
```

## How It Works

1. **GitHub Actions** runs every 4 hours
2. **Python script** fetches prices from GoodReturns.in
3. **Data is saved** to `data/prices.json`
4. **Website displays** the data with charts and tables

## Customization

### Change Update Frequency

Edit `.github/workflows/update-prices.yml`:

```yaml
schedule:
  # Every 4 hours (default)
  - cron: '0 */4 * * *'
  
  # Every hour
  # - cron: '0 * * * *'
  
  # Every 6 hours
  # - cron: '0 */6 * * *'
```

### Add More Cities

Edit `scripts/fetch_prices.py` and add new URLs:

```python
CITIES = {
    'hyderabad': 'https://www.goodreturns.in/gold-rates/hyderabad.html',
    'mumbai': 'https://www.goodreturns.in/gold-rates/mumbai.html',
    # Add more cities
}
```

### Change Styling

Edit `style.css` to customize colors and fonts:

```css
:root {
    --accent-green: #10b981;  /* Price up color */
    --accent-red: #ef4444;    /* Price down color */
    --accent-blue: #6366f1;   /* Accent color */
}
```

## Data Source

Gold prices are sourced from [GoodReturns.in](https://www.goodreturns.in), a trusted Indian financial website.

**Note**: Prices are indicative and may vary slightly from actual market rates. Always verify with your local jeweler before making purchase decisions.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Data provided by [GoodReturns.in](https://www.goodreturns.in)
- Charts powered by [Chart.js](https://www.chartjs.org/)
- Built with vanilla HTML, CSS, and JavaScript

## Support

If you find this helpful, consider:
- Starring the repository
- Sharing with family and friends
- Contributing improvements

---

**Disclaimer**: This is an unofficial tool for informational purposes only. Gold prices shown are approximate and may not reflect real-time market rates. Please consult authorized dealers for actual prices.
