# calculator_mcp

Basic MCP calculator server with tools:
- `add`
- `subtract`
- `multiply`
- `divide`

## Run

```bash
npm install
npm start
```

## Configuration

Set `SUPPORTED_DATA_TYPE` to control accepted input types:
- `integer` - only integer inputs
- `decimal` - only decimal (non-integer) inputs
- `both` - accepts integer and decimal inputs (default)
