import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DataPoint {
    x: number;
    y: number;
}

interface ScatterPlotProps {
    data: DataPoint[];
}

export const ScatterPlot: React.FC<ScatterPlotProps> = ({ data }) => {
    if (data.length === 0) {
        return <div className="text-gray-500 italic">No hay datos para mostrar.</div>;
    }

    return (
        <div className="scatterplot-container">
            <h3 className="chart-title">Scatterplot Dataset</h3>
            <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart
                        margin={{
                            top: 20,
                            right: 20,
                            bottom: 20,
                            left: 20,
                        }}
                    >
                        <CartesianGrid />
                        <XAxis type="number" dataKey="x" name="X" />
                        <YAxis type="number" dataKey="y" name="Y" />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                        <Scatter name="Data" data={data} fill="#8884d8" />
                    </ScatterChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
