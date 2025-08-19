# 🚀 Local Development Guide

## Quick Start

### Option 1: Use the startup script (Recommended)
```bash
./start.sh
```

### Option 2: Manual startup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## 🌐 Access Your App

Once running, your app will be available at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://192.168.x.x:8501 (for testing on other devices)

## 🛠️ Development Workflow

1. **Edit** `streamlit_app.py` in your favorite editor
2. **Save** the file - Streamlit auto-reloads!
3. **Test** changes immediately in the browser
4. **Commit** when ready: `git add . && git commit -m "message"`

## 📦 Dependencies

The app requires these Python packages (automatically installed):
- `streamlit` - Web app framework
- `pandas` - Data manipulation
- `plotly` - Interactive charts
- `numpy` - Numerical operations

## 🔧 Troubleshooting

### Port already in use?
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Python not found?
```bash
# Install Python 3.8+ from python.org
# Or use Homebrew on Mac:
brew install python
```

### Dependencies issues?
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt --force-reinstall
```

## 🚀 Deployment

When ready to deploy:
1. **Test locally** first
2. **Commit changes**: `git push origin main`
3. **Deploy on Streamlit**: [share.streamlit.io](https://share.streamlit.io)

## 💡 Tips

- **Auto-reload**: Streamlit automatically reloads when you save files
- **Hot reload**: Browser refreshes automatically
- **Debug mode**: Use `st.write()` for debugging
- **Performance**: Large datasets? Use `st.cache_data` decorator

Happy coding! 🎉
