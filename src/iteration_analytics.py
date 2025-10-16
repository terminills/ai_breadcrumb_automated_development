"""
Enhanced Analytics for Copilot Iteration System

Provides detailed analytics and visualization of iteration performance,
patterns, and trends.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class IterationAnalytics:
    """
    Analytics engine for copilot iteration system
    Provides insights, trends, and performance metrics
    """
    
    def __init__(self, iteration_history: List[Dict[str, Any]], learned_patterns: Dict[str, Any]):
        """
        Initialize analytics with iteration history and learned patterns
        
        Args:
            iteration_history: List of completed iterations
            learned_patterns: Dictionary of learned patterns by phase
        """
        self.iteration_history = iteration_history
        self.learned_patterns = learned_patterns
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.iteration_history:
            return {
                'total_iterations': 0,
                'message': 'No iteration history available'
            }
        
        successful = [h for h in self.iteration_history if h['success']]
        failed = [h for h in self.iteration_history if not h['success']]
        
        summary = {
            'total_iterations': len(self.iteration_history),
            'successful_iterations': len(successful),
            'failed_iterations': len(failed),
            'success_rate': len(successful) / len(self.iteration_history),
            'average_time': sum(h['total_time'] for h in self.iteration_history) / len(self.iteration_history),
            'average_retries': sum(h['retry_count'] for h in self.iteration_history) / len(self.iteration_history),
            'total_time': sum(h['total_time'] for h in self.iteration_history),
        }
        
        # Calculate time breakdown by phase
        phase_times = {}
        for history in self.iteration_history:
            for phase, time in history.get('timings', {}).items():
                if phase not in phase_times:
                    phase_times[phase] = []
                phase_times[phase].append(time)
        
        summary['phase_timings'] = {
            phase: {
                'average': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'total': sum(times)
            }
            for phase, times in phase_times.items()
        }
        
        # Success rate over time (last 10 iterations)
        recent = self.iteration_history[-10:]
        summary['recent_success_rate'] = sum(1 for h in recent if h['success']) / len(recent) if recent else 0
        
        return summary
    
    def get_phase_analysis(self, phase: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze performance for a specific phase or all phases
        
        Args:
            phase: Optional phase name (analyzes all if not provided)
            
        Returns:
            Dictionary with phase-specific analysis
        """
        if phase:
            # Analyze specific phase
            if phase not in self.learned_patterns:
                return {
                    'phase': phase,
                    'message': f'No data available for phase {phase}'
                }
            
            pattern = self.learned_patterns[phase]
            phase_history = [
                h for h in self.iteration_history
                if h.get('phase') == phase
            ]
            
            analysis = {
                'phase': phase,
                'total_attempts': pattern['total_attempts'],
                'successes': pattern['successes'],
                'success_rate': pattern['successes'] / pattern['total_attempts'],
                'avg_retries': pattern['avg_retries'],
                'avg_time': pattern['avg_time'],
                'iterations': len(phase_history)
            }
            
            # Calculate trend (improving or declining)
            if len(phase_history) >= 3:
                recent = phase_history[-3:]
                earlier = phase_history[-6:-3] if len(phase_history) >= 6 else phase_history[:-3]
                
                recent_success = sum(1 for h in recent if h['success']) / len(recent)
                earlier_success = sum(1 for h in earlier if h['success']) / len(earlier) if earlier else 0
                
                if recent_success > earlier_success + 0.1:
                    analysis['trend'] = 'improving'
                elif recent_success < earlier_success - 0.1:
                    analysis['trend'] = 'declining'
                else:
                    analysis['trend'] = 'stable'
            else:
                analysis['trend'] = 'insufficient_data'
            
            return analysis
        else:
            # Analyze all phases
            return {
                phase: self.get_phase_analysis(phase)
                for phase in self.learned_patterns.keys()
            }
    
    def get_time_series_analysis(self) -> Dict[str, Any]:
        """
        Analyze iterations over time to identify trends
        
        Returns:
            Dictionary with time series analysis
        """
        if not self.iteration_history:
            return {'message': 'No iteration history available'}
        
        # Group by iteration number
        iterations = sorted(self.iteration_history, key=lambda x: x['iteration'])
        
        time_series = {
            'iterations': [h['iteration'] for h in iterations],
            'success': [1 if h['success'] else 0 for h in iterations],
            'retry_count': [h['retry_count'] for h in iterations],
            'total_time': [h['total_time'] for h in iterations],
        }
        
        # Calculate moving averages (window of 3)
        if len(iterations) >= 3:
            moving_avg_success = []
            for i in range(len(iterations)):
                start = max(0, i - 2)
                window = iterations[start:i+1]
                moving_avg_success.append(
                    sum(1 for h in window if h['success']) / len(window)
                )
            time_series['moving_avg_success'] = moving_avg_success
        
        return time_series
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """
        Analyze errors and their patterns
        
        Returns:
            Dictionary with error analysis
        """
        error_stats = {
            'total_failures': 0,
            'error_types': {},
            'most_common_errors': [],
            'phases_with_most_errors': []
        }
        
        # Collect errors from failed iterations
        for history in self.iteration_history:
            if not history['success']:
                error_stats['total_failures'] += 1
                
                # Count errors by type
                errors = history.get('compilation', {}).get('errors', [])
                for error in errors:
                    # Extract error type (simple heuristic)
                    error_type = 'unknown'
                    if 'syntax' in error.lower():
                        error_type = 'syntax'
                    elif 'undefined' in error.lower():
                        error_type = 'undefined_reference'
                    elif 'type' in error.lower():
                        error_type = 'type_error'
                    elif 'segmentation' in error.lower() or 'segfault' in error.lower():
                        error_type = 'runtime_error'
                    
                    error_stats['error_types'][error_type] = error_stats['error_types'].get(error_type, 0) + 1
        
        # Find most common errors
        if error_stats['error_types']:
            sorted_errors = sorted(
                error_stats['error_types'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            error_stats['most_common_errors'] = [
                {'type': err_type, 'count': count}
                for err_type, count in sorted_errors[:5]
            ]
        
        # Find phases with most errors
        phase_errors = {}
        for history in self.iteration_history:
            if not history['success']:
                phase = history.get('phase', 'unknown')
                phase_errors[phase] = phase_errors.get(phase, 0) + 1
        
        if phase_errors:
            sorted_phases = sorted(
                phase_errors.items(),
                key=lambda x: x[1],
                reverse=True
            )
            error_stats['phases_with_most_errors'] = [
                {'phase': phase, 'count': count}
                for phase, count in sorted_phases[:5]
            ]
        
        return error_stats
    
    def get_recommendations(self) -> List[str]:
        """
        Generate actionable recommendations based on analytics
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        summary = self.get_performance_summary()
        
        # Success rate recommendations
        if summary.get('success_rate', 0) < 0.5:
            recommendations.append(
                f"⚠️ Low success rate ({summary['success_rate']*100:.0f}%). "
                "Consider increasing exploration depth or adjusting model parameters."
            )
        elif summary.get('success_rate', 0) >= 0.8:
            recommendations.append(
                f"✓ Excellent success rate ({summary['success_rate']*100:.0f}%). "
                "Current approach is working well."
            )
        
        # Retry recommendations
        if summary.get('average_retries', 0) > 2.5:
            recommendations.append(
                f"⚠️ High average retries ({summary['average_retries']:.1f}). "
                "Tasks may be too complex or exploration may be insufficient."
            )
        
        # Time recommendations
        if summary.get('average_time', 0) > 120:
            recommendations.append(
                f"⏱️ Long average iteration time ({summary['average_time']:.0f}s). "
                "Consider optimizing slow phases or using smaller models for exploration."
            )
        
        # Trend recommendations
        if summary.get('recent_success_rate', 0) < summary.get('success_rate', 0) - 0.15:
            recommendations.append(
                "📉 Recent success rate is declining. "
                "Review recent changes and consider rolling back to previous approach."
            )
        elif summary.get('recent_success_rate', 0) > summary.get('success_rate', 0) + 0.15:
            recommendations.append(
                "📈 Recent success rate is improving! "
                "Current approach is learning and adapting well."
            )
        
        # Phase-specific recommendations
        for phase, pattern in self.learned_patterns.items():
            if pattern['total_attempts'] >= 3:
                success_rate = pattern['successes'] / pattern['total_attempts']
                if success_rate < 0.3:
                    recommendations.append(
                        f"⚠️ Phase '{phase}' has low success rate ({success_rate*100:.0f}%). "
                        f"Consider specialized approach or additional training for this phase."
                    )
        
        if not recommendations:
            recommendations.append(
                "✓ All metrics look good. Continue with current approach."
            )
        
        return recommendations
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive analytics report
        
        Args:
            output_path: Optional path to save report (prints to console if not provided)
            
        Returns:
            Report as formatted string
        """
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("  Copilot Iteration Analytics Report")
        report_lines.append("=" * 70)
        report_lines.append("")
        
        # Performance summary
        report_lines.append("## Performance Summary")
        report_lines.append("-" * 70)
        summary = self.get_performance_summary()
        
        if summary.get('total_iterations', 0) > 0:
            report_lines.append(f"Total Iterations: {summary['total_iterations']}")
            report_lines.append(f"Successful: {summary['successful_iterations']} ({summary['success_rate']*100:.1f}%)")
            report_lines.append(f"Failed: {summary['failed_iterations']}")
            report_lines.append(f"Average Time: {summary['average_time']:.1f}s")
            report_lines.append(f"Average Retries: {summary['average_retries']:.1f}")
            report_lines.append(f"Total Time Spent: {summary['total_time']:.0f}s ({summary['total_time']/60:.1f}m)")
            report_lines.append("")
            
            # Phase timings
            if summary.get('phase_timings'):
                report_lines.append("### Time by Phase")
                for phase, timings in summary['phase_timings'].items():
                    report_lines.append(f"  {phase}:")
                    report_lines.append(f"    Average: {timings['average']:.1f}s")
                    report_lines.append(f"    Range: {timings['min']:.1f}s - {timings['max']:.1f}s")
                report_lines.append("")
        else:
            report_lines.append("No iteration data available.")
            report_lines.append("")
        
        # Phase analysis
        report_lines.append("## Phase Analysis")
        report_lines.append("-" * 70)
        phase_analysis = self.get_phase_analysis()
        
        for phase, analysis in phase_analysis.items():
            if 'message' in analysis:
                continue
            report_lines.append(f"### {phase}")
            report_lines.append(f"  Success Rate: {analysis['success_rate']*100:.1f}% ({analysis['successes']}/{analysis['total_attempts']})")
            report_lines.append(f"  Average Retries: {analysis['avg_retries']:.1f}")
            report_lines.append(f"  Average Time: {analysis['avg_time']:.1f}s")
            report_lines.append(f"  Trend: {analysis['trend']}")
            report_lines.append("")
        
        # Error analysis
        report_lines.append("## Error Analysis")
        report_lines.append("-" * 70)
        error_analysis = self.get_error_analysis()
        
        report_lines.append(f"Total Failures: {error_analysis['total_failures']}")
        
        if error_analysis.get('most_common_errors'):
            report_lines.append("\n### Most Common Errors:")
            for error in error_analysis['most_common_errors']:
                report_lines.append(f"  - {error['type']}: {error['count']} occurrences")
        
        if error_analysis.get('phases_with_most_errors'):
            report_lines.append("\n### Phases with Most Errors:")
            for phase_err in error_analysis['phases_with_most_errors']:
                report_lines.append(f"  - {phase_err['phase']}: {phase_err['count']} failures")
        
        report_lines.append("")
        
        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("-" * 70)
        for recommendation in self.get_recommendations():
            report_lines.append(f"• {recommendation}")
        
        report_lines.append("")
        report_lines.append("=" * 70)
        report_lines.append(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 70)
        
        report = "\n".join(report_lines)
        
        # Save to file if path provided
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    f.write(report)
                logger.info(f"Analytics report saved to {output_path}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")
        
        return report
