#!/usr/bin/env python3
"""
Debug D3.js rendering issues and create a diagnostic version
"""
import sys
sys.path.append('.')

def create_d3_diagnostic_template():
    """Create a minimal D3.js diagnostic template."""
    diagnostic_content = '''{% extends "streamlined_base.html" %}

{% block title %}D3.js Diagnostic - PRISM | MaLDReTH II RDA{% endblock %}

{% block extra_head %}
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
    .diagnostic-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    
    .status-item {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        font-family: monospace;
    }
    
    .success { background-color: #d4edda; color: #155724; }
    .error { background-color: #f8d7da; color: #721c24; }
    .warning { background-color: #fff3cd; color: #856404; }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-12">
            <h1 class="display-4 text-primary mb-3">
                <i class="fas fa-bug me-3"></i>D3.js Diagnostic Tool
            </h1>
            <p class="lead text-muted">
                Testing D3.js functionality and identifying rendering issues
            </p>
        </div>
    </div>

    <div class="row">
        <div class="col-lg-6">
            <div class="diagnostic-container">
                <h3>Environment Checks</h3>
                <div id="environment-status">
                    <div class="status-item">🔍 Running diagnostics...</div>
                </div>
            </div>
            
            <div class="diagnostic-container">
                <h3>D3.js Functionality Test</h3>
                <div id="d3-status">
                    <div class="status-item">🔍 Testing D3.js...</div>
                </div>
            </div>
        </div>
        
        <div class="col-lg-6">
            <div class="diagnostic-container">
                <h3>Simple D3 Visualization Test</h3>
                <svg id="test-svg" width="400" height="300" style="border: 1px solid #ddd; background: white;"></svg>
                <div id="svg-status" class="mt-2">
                    <div class="status-item">🔍 Creating test visualization...</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-12">
            <div class="diagnostic-container">
                <h3>Console Output</h3>
                <pre id="console-output" style="max-height: 300px; overflow-y: auto; background: #333; color: #fff; padding: 1rem; border-radius: 5px;">
Starting diagnostic...
                </pre>
            </div>
        </div>
    </div>
</div>

<script>
// Diagnostic logging function
function logDiagnostic(message, type = 'info') {
    const output = document.getElementById('console-output');
    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ${type.toUpperCase()}: ${message}\\n`;
    output.textContent += logMessage;
    output.scrollTop = output.scrollHeight;
    console.log(logMessage);
}

// Override console methods to capture errors
const originalError = console.error;
console.error = function(...args) {
    logDiagnostic(args.join(' '), 'error');
    originalError.apply(console, args);
};

document.addEventListener('DOMContentLoaded', function() {
    logDiagnostic('DOM Content Loaded');
    
    // 1. Environment Checks
    const envStatus = document.getElementById('environment-status');
    let envChecks = [];
    
    // Check if we're in a browser
    if (typeof window !== 'undefined') {
        envChecks.push('<div class="status-item success">✅ Running in browser environment</div>');
    } else {
        envChecks.push('<div class="status-item error">❌ Not in browser environment</div>');
    }
    
    // Check if D3 is loaded
    if (typeof d3 !== 'undefined') {
        envChecks.push(`<div class="status-item success">✅ D3.js loaded (version ${d3.version || 'unknown'})</div>`);
        logDiagnostic(`D3.js version: ${d3.version || 'unknown'}`);
    } else {
        envChecks.push('<div class="status-item error">❌ D3.js not loaded</div>');
        logDiagnostic('D3.js not loaded', 'error');
    }
    
    // Check SVG support
    const svgSupported = document.createElementNS && document.createElementNS('http://www.w3.org/2000/svg', 'svg').createSVGRect;
    if (svgSupported) {
        envChecks.push('<div class="status-item success">✅ SVG support available</div>');
    } else {
        envChecks.push('<div class="status-item error">❌ SVG support missing</div>');
    }
    
    envStatus.innerHTML = envChecks.join('');
    
    // 2. D3.js Functionality Tests
    const d3Status = document.getElementById('d3-status');
    let d3Checks = [];
    
    try {
        if (typeof d3 !== 'undefined') {
            // Test basic D3 selection
            const testDiv = d3.select('body');
            if (testDiv.node()) {
                d3Checks.push('<div class="status-item success">✅ D3 selection works</div>');
                logDiagnostic('D3 selection test passed');
            } else {
                d3Checks.push('<div class="status-item error">❌ D3 selection failed</div>');
                logDiagnostic('D3 selection test failed', 'error');
            }
            
            // Test D3 data binding
            const testData = [1, 2, 3];
            const testBinding = d3.selectAll('.test-data-binding').data(testData);
            d3Checks.push('<div class="status-item success">✅ D3 data binding works</div>');
            logDiagnostic('D3 data binding test passed');
            
            // Test SVG creation
            const testSvg = d3.select('#test-svg');
            if (testSvg.node()) {
                d3Checks.push('<div class="status-item success">✅ D3 SVG selection works</div>');
                logDiagnostic('D3 SVG selection test passed');
                
                // Try to create a simple shape
                try {
                    testSvg.append('circle')
                        .attr('cx', 50)
                        .attr('cy', 50)
                        .attr('r', 20)
                        .attr('fill', 'steelblue');
                    
                    testSvg.append('text')
                        .attr('x', 50)
                        .attr('y', 100)
                        .attr('text-anchor', 'middle')
                        .text('D3 Test Circle');
                    
                    d3Checks.push('<div class="status-item success">✅ D3 SVG element creation works</div>');
                    logDiagnostic('D3 SVG element creation test passed');
                    
                    document.getElementById('svg-status').innerHTML = '<div class="status-item success">✅ Simple visualization created successfully</div>';
                    
                } catch (error) {
                    d3Checks.push(`<div class="status-item error">❌ D3 SVG element creation failed: ${error.message}</div>`);
                    logDiagnostic(`D3 SVG element creation failed: ${error.message}`, 'error');
                    document.getElementById('svg-status').innerHTML = `<div class="status-item error">❌ Visualization failed: ${error.message}</div>`;
                }
                
            } else {
                d3Checks.push('<div class="status-item error">❌ D3 SVG selection failed</div>');
                logDiagnostic('D3 SVG selection failed', 'error');
            }
            
        } else {
            d3Checks.push('<div class="status-item error">❌ D3.js not available for testing</div>');
        }
        
    } catch (error) {
        d3Checks.push(`<div class="status-item error">❌ D3 functionality test failed: ${error.message}</div>`);
        logDiagnostic(`D3 functionality test failed: ${error.message}`, 'error');
    }
    
    d3Status.innerHTML = d3Checks.join('');
    
    logDiagnostic('Diagnostic complete');
});

// Catch any unhandled errors
window.addEventListener('error', function(event) {
    logDiagnostic(`Unhandled error: ${event.error ? event.error.message : event.message}`, 'error');
});

// Catch any unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    logDiagnostic(`Unhandled promise rejection: ${event.reason}`, 'error');
});

</script>
{% endblock %}'''

    with open('/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/templates/d3_diagnostic.html', 'w') as f:
        f.write(diagnostic_content)
    
    print("✅ Created D3.js diagnostic template")

def add_diagnostic_route():
    """Add route for D3.js diagnostic page."""
    route_code = '''
@app.route('/d3-diagnostic')
def d3_diagnostic():
    """Diagnostic page for D3.js issues."""
    return render_template('d3_diagnostic.html')
'''
    
    # Add to streamlined_app.py
    with open('/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/streamlined_app.py', 'r') as f:
        content = f.read()
    
    # Insert before the last few lines
    insert_point = content.rfind('if __name__ == "__main__":')
    if insert_point != -1:
        new_content = content[:insert_point] + route_code + '\n' + content[insert_point:]
        
        with open('/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/streamlined_app.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Added D3.js diagnostic route to streamlined_app.py")
    else:
        print("❌ Could not find insertion point in streamlined_app.py")

def main():
    print("Creating D3.js Diagnostic Tools")
    print("=" * 40)
    
    create_d3_diagnostic_template()
    add_diagnostic_route()
    
    print("\n📋 Next Steps:")
    print("1. Deploy to Heroku: git add . && git commit -m 'Add D3 diagnostic' && git push heroku main")
    print("2. Visit: https://mal2-data-survey-cb27f6674f20.herokuapp.com/d3-diagnostic")
    print("3. Check browser console and diagnostic output")

if __name__ == "__main__":
    main()