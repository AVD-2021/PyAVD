mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"raihaan.usman19@imperial.ac.uk\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml

echo "\
[theme]\n\
base="dark"\n\
secondaryBackgroundColor="#3d0811"\n\
" > ~/.streamlit/config.toml
