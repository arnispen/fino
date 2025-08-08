import typer
from ..utils import get_config_value, set_config_value, load_config

app = typer.Typer(help="Manage global configuration")

@app.command()
def set(
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Option(None, "--value", "-v", help="Value to set (if not provided, will prompt)"),
):
    """
    Set a configuration value.
    
    Examples:
        fino config set pinata-jwt
        fino config set pinata-jwt --value your_jwt_token
    """
    if value is None:
        if key == "pinata-jwt":
            typer.secho("🔑 Pinata JWT Configuration", fg=typer.colors.CYAN)
            typer.secho("=" * 40, fg=typer.colors.CYAN)
            typer.secho("1. Go to https://app.pinata.cloud/", fg=typer.colors.YELLOW)
            typer.secho("2. Sign in and go to API Keys", fg=typer.colors.YELLOW)
            typer.secho("3. Create a new API key", fg=typer.colors.YELLOW)
            typer.secho("4. Copy the JWT token", fg=typer.colors.YELLOW)
            typer.secho("=" * 40, fg=typer.colors.CYAN)
            value = typer.prompt("Enter your Pinata JWT token", hide_input=True)
        else:
            value = typer.prompt(f"Enter value for {key}")
    
    # Convert kebab-case to snake_case for storage
    storage_key = key.replace("-", "_")
    set_config_value(storage_key, value)
    
    typer.secho(f"✅ {key} configured successfully!", fg=typer.colors.GREEN)
    typer.secho(f"   Value: {value[:8]}..." if len(value) > 8 else f"   Value: {value}", fg=typer.colors.CYAN)

@app.command()
def get(
    key: str = typer.Argument(..., help="Configuration key to get"),
):
    """
    Get a configuration value.
    
    Examples:
        fino config get pinata-jwt
    """
    # Convert kebab-case to snake_case for lookup
    storage_key = key.replace("-", "_")
    value = get_config_value(storage_key)
    
    if value:
        typer.secho(f"📋 {key}: {value[:8]}..." if len(value) > 8 else f"📋 {key}: {value}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"❌ {key} not configured", fg=typer.colors.RED)

@app.command()
def list():
    """
    List all configuration values.
    """
    config = load_config()
    
    if not config:
        typer.secho("📋 No configuration values set", fg=typer.colors.YELLOW)
        return
    
    typer.secho("📋 Configuration Values:", fg=typer.colors.CYAN)
    typer.secho("=" * 30, fg=typer.colors.CYAN)
    
    for key, value in config.items():
        display_key = key.replace("_", "-")
        display_value = value[:8] + "..." if len(value) > 8 else value
        typer.secho(f"  {display_key}: {display_value}", fg=typer.colors.GREEN)

@app.command()
def unset(
    key: str = typer.Argument(..., help="Configuration key to remove"),
):
    """
    Remove a configuration value.
    
    Examples:
        fino config unset pinata-jwt
    """
    from ..utils import load_config, save_config
    
    config = load_config()
    storage_key = key.replace("-", "_")
    
    if storage_key in config:
        del config[storage_key]
        save_config(config)
        typer.secho(f"✅ {key} removed from configuration", fg=typer.colors.GREEN)
    else:
        typer.secho(f"❌ {key} not found in configuration", fg=typer.colors.RED) 