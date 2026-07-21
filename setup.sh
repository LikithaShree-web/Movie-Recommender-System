mkdir -p ~/.streamlit/

echo "\
[server]
port = $PORT
headless = true
enableCORS = false
" > ~/.streamlit/config.toml