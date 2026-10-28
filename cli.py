#!/usr/bin/env python3
"""FreeNode CLI - Main entry point"""

import click
import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import Detector, Profiler, Orchestrator, Monitor, Persistence

@click.group()
def cli():
    """FreeNode - Universal Platform Bypass Framework"""
    pass

@cli.command()
def diagnose():
    """Detect environment and show platform profile"""
    click.echo("🔍 Diagnosing environment...")
    
    detector = Detector()
    env = detector.detect_all()
    
    click.echo("\n📊 Environment Detection:")
    click.echo(json.dumps(env, indent=2))
    
    profiler = Profiler(env)
    profile = profiler.generate_profile()
    
    click.echo("\n🎯 Platform Profile:")
    click.echo(json.dumps(profile, indent=2))
    
    orchestrator = Orchestrator(profile)
    strategy = orchestrator.full_strategy()
    
    click.echo("\n⚙️  Strategy:")
    click.echo(json.dumps(strategy, indent=2))

@cli.command()
@click.option('--platform', default=None, help='Target platform (auto-detect if not provided)')
def init(platform):
    """Initialize FreeNode for current environment"""
    click.echo("🚀 Initializing FreeNode...")
    
    detector = Detector()
    env = detector.detect_all()
    
    profiler = Profiler(env)
    profile = profiler.generate_profile()
    
    orchestrator = Orchestrator(profile)
    strategy = orchestrator.full_strategy()
    
    # Create state directory
    os.makedirs('freenode/state', exist_ok=True)
    
    # Save profile
    with open('freenode/state/profile.json', 'w') as f:
        json.dump(profile, f, indent=2)
    
    # Save strategy
    with open('freenode/state/strategy.json', 'w') as f:
        json.dump(strategy, f, indent=2)
    
    click.echo("\n✅ FreeNode initialized!")
    click.echo(f"   Platform: {profile['platform']}")
    click.echo(f"   Class: {profile['class']}")
    click.echo(f"   Modules: {', '.join(profile['modules'])}")
    click.echo("\n📝 Run 'freenode start' to activate modules")

@cli.command()
def start():
    """Start all modules for current environment"""
    click.echo("▶️  Starting FreeNode modules...")
    
    if not os.path.exists('freenode/state/strategy.json'):
        click.echo("❌ No strategy found. Run 'freenode init' first.")
        return
    
    with open('freenode/state/strategy.json', 'r') as f:
        strategy = json.load(f)
    
    monitor = Monitor(strategy)
    health = monitor.start_all()
    
    click.echo("\n📊 Module Health:")
    for module, status in health.items():
        status_icon = "✅" if status else "❌"
        click.echo(f"   {status_icon} {module}")

@cli.command()
def status():
    """Show current FreeNode status"""
    if not os.path.exists('freenode/state/strategy.json'):
        click.echo("❌ FreeNode not initialized. Run 'freenode init' first.")
        return
    
    with open('freenode/state/strategy.json', 'r') as f:
        strategy = json.load(f)
    
    click.echo("📊 FreeNode Status:")
    click.echo(json.dumps(strategy, indent=2))

@cli.command()
@click.argument('platform')
def test(platform):
    """Run platform test and archive results"""
    click.echo(f"🧪 Testing platform: {platform}")
    
    detector = Detector()
    env = detector.detect_all()
    
    profiler = Profiler(env)
    profile = profiler.generate_profile()
    
    # Create test result
    result = {
        'test_id': f"{platform}-001",
        'platform': platform,
        'environment': env,
        'profile': profile,
        'status': 'pending'
    }
    
    # Save test result
    os.makedirs('tests/results', exist_ok=True)
    with open(f'tests/results/{platform}-test.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    click.echo(f"✅ Test result saved to tests/results/{platform}-test.json")

if __name__ == '__main__':
    cli()
