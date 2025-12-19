
import React, { useState, useEffect } from 'react';

const AssetMapper = () => {
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(false);

    // Slicer State
    const [sliceTarget, setSliceTarget] = useState(null);
    const [cols, setCols] = useState(6);
    const [rows, setRows] = useState(4);
    const [padding, setPadding] = useState(0);
    const [slicing, setSlicing] = useState(false);

    const fetchAssets = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/assets');
            const data = await response.json();
            setAssets(data.assets || []);
        } catch (error) {
            console.error("Failed to fetch assets:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAssets();
    }, []);

    return (
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 h-full overflow-y-auto">
            <h2 className="text-xl font-bold text-white mb-4">Asset Manager</h2>
            <p className="text-gray-400 text-sm mb-4">
                Drop images into <code>data/assets</code> to see them here.
            </p>

            <button
                onClick={fetchAssets}
                className="mb-4 px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm transition-colors"
            >
                Refresh Assets
            </button>

            {loading ? (
                <div className="text-gray-500">Loading...</div>
            ) : (
                <div className="grid grid-cols-2 gap-4">
                    {assets.length === 0 ? (
                        <p className="col-span-2 text-gray-500 italic">No assets found.</p>
                    ) : (
                        assets.map((asset, index) => (
                            <div key={index} className="bg-gray-900 p-2 rounded hover:ring-2 ring-blue-500 cursor-pointer group relative">
                                <div className="aspect-square bg-black mb-2 rounded overflow-hidden flex items-center justify-center">
                                    <img
                                        src={`http://localhost:8000${asset}`}
                                        alt={asset}
                                        className="max-w-full max-h-full object-contain"
                                    />
                                </div>
                                <p className="text-xs text-gray-300 truncate" title={asset}>
                                    {asset.split('/').pop()}
                                </p>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setSliceTarget(asset);
                                    }}
                                    className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 bg-gray-700 hover:bg-gray-600 text-white text-[10px] px-2 py-1 rounded"
                                >
                                    ✂ Slice
                                </button>
                            </div>
                        ))
                    )}
                </div>
            )}
            {/* Slicer Modal */}
            {sliceTarget && (
                <div className="absolute inset-0 z-50 bg-black/90 flex items-center justify-center p-4">
                    <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full border border-gray-600">
                        <h3 className="text-xl font-bold text-white mb-4">Slice {sliceTarget.split('/').pop()}</h3>

                        <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Columns</label>
                                <input
                                    type="number"
                                    value={cols}
                                    onChange={(e) => setCols(parseInt(e.target.value) || 1)}
                                    className="w-full bg-gray-900 border border-gray-700 text-white px-2 py-1 rounded"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Rows</label>
                                <input
                                    type="number"
                                    value={rows}
                                    onChange={(e) => setRows(parseInt(e.target.value) || 1)}
                                    className="w-full bg-gray-900 border border-gray-700 text-white px-2 py-1 rounded"
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-xs text-gray-400 mb-1">Padding (px)</label>
                                <input
                                    type="number"
                                    value={padding}
                                    onChange={(e) => setPadding(parseInt(e.target.value) || 0)}
                                    className="w-full bg-gray-900 border border-gray-700 text-white px-2 py-1 rounded"
                                />
                            </div>
                        </div>

                        <div className="flex justify-end gap-2 mt-6">
                            <button
                                onClick={() => setSliceTarget(null)}
                                className="px-4 py-2 text-gray-300 hover:text-white"
                                disabled={slicing}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={async () => {
                                    setSlicing(true);
                                    try {
                                        await fetch('http://localhost:8000/api/assets/slice', {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify({
                                                filename: sliceTarget,
                                                cols, rows, padding
                                            })
                                        });
                                        setSliceTarget(null);
                                        fetchAssets(); // Refresh to see slices
                                    } catch (err) {
                                        alert("Slice failed: " + err);
                                    } finally {
                                        setSlicing(false);
                                    }
                                }}
                                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded font-bold"
                                disabled={slicing}
                            >
                                {slicing ? "Slicing..." : "⚡ Slice Now"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AssetMapper;
