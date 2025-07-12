#!/usr/bin/env python3
"""
Generate PWA icons using SVG and convert to PNG
"""

import os
from xml.etree.ElementTree import Element, SubElement, tostring

def create_icon_svg(size):
    """Create an SVG icon for the data analysis app"""
    svg = Element('svg')
    svg.set('width', str(size))
    svg.set('height', str(size))
    svg.set('viewBox', '0 0 100 100')
    svg.set('xmlns', 'http://www.w3.org/2000/svg')
    
    # Background gradient
    defs = SubElement(svg, 'defs')
    gradient = SubElement(defs, 'linearGradient')
    gradient.set('id', 'grad1')
    gradient.set('x1', '0%')
    gradient.set('y1', '0%')
    gradient.set('x2', '100%')
    gradient.set('y2', '100%')
    
    stop1 = SubElement(gradient, 'stop')
    stop1.set('offset', '0%')
    stop1.set('style', 'stop-color:#667eea;stop-opacity:1')
    
    stop2 = SubElement(gradient, 'stop')
    stop2.set('offset', '100%')
    stop2.set('style', 'stop-color:#764ba2;stop-opacity:1')
    
    # Background circle
    circle = SubElement(svg, 'circle')
    circle.set('cx', '50')
    circle.set('cy', '50')
    circle.set('r', '45')
    circle.set('fill', 'url(#grad1)')
    
    # Chart bars
    rect1 = SubElement(svg, 'rect')
    rect1.set('x', '25')
    rect1.set('y', '60')
    rect1.set('width', '8')
    rect1.set('height', '20')
    rect1.set('fill', 'white')
    rect1.set('rx', '2')
    
    rect2 = SubElement(svg, 'rect')
    rect2.set('x', '38')
    rect2.set('y', '45')
    rect2.set('width', '8')
    rect2.set('height', '35')
    rect2.set('fill', 'white')
    rect2.set('rx', '2')
    
    rect3 = SubElement(svg, 'rect')
    rect3.set('x', '51')
    rect3.set('y', '35')
    rect3.set('width', '8')
    rect3.set('height', '45')
    rect3.set('fill', 'white')
    rect3.set('rx', '2')
    
    rect4 = SubElement(svg, 'rect')
    rect4.set('x', '64')
    rect4.set('y', '50')
    rect4.set('width', '8')
    rect4.set('height', '30')
    rect4.set('fill', 'white')
    rect4.set('rx', '2')
    
    # Trend line
    path = SubElement(svg, 'path')
    path.set('d', 'M 20 70 Q 35 55 50 40 T 80 45')
    path.set('stroke', 'white')
    path.set('stroke-width', '2')
    path.set('fill', 'none')
    path.set('opacity', '0.8')
    
    return tostring(svg, encoding='unicode')

def generate_icons():
    """Generate all required icon sizes"""
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        svg_content = create_icon_svg(size)
        filename = f'icon-{size}x{size}.svg'
        
        with open(filename, 'w') as f:
            f.write(svg_content)
        
        print(f'Generated {filename}')

if __name__ == '__main__':
    generate_icons()