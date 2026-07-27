import type { ReactNode } from 'react';
import { COLORS } from '../styles/theme';

interface DataTableProps {
  data: Record<string, unknown>[];
  columns: string[];
  maxRows?: number;
}

function cellContent(column: string, value: unknown): ReactNode {
  const display = String(value ?? '');
  if ((column === 'drugId' || column === 'Drug') && display.startsWith('CHEMBL')) {
    return (
      <a
        href={`https://www.ebi.ac.uk/chembl/compound_report_card/${encodeURIComponent(display)}`}
        target="_blank"
        rel="noopener noreferrer"
        className="hover:underline"
        style={{ color: COLORS.primary }}
      >
        {display}
      </a>
    );
  }
  if (column === 'Gene' && display && display !== 'null' && display !== 'nan') {
    return (
      <a
        href={`https://www.uniprot.org/uniprotkb?query=${encodeURIComponent(`gene:${display} AND organism_id:9606`)}`}
        target="_blank"
        rel="noopener noreferrer"
        className="hover:underline"
        style={{ color: COLORS.primary }}
      >
        {display}
      </a>
    );
  }
  if ((column === 'ICD10' || column === 'icd_code') && display && display !== 'null') {
    return (
      <a
        href={`https://icd.who.int/browse10/2019/en#/${encodeURIComponent(display)}`}
        target="_blank"
        rel="noopener noreferrer"
        className="hover:underline"
        style={{ color: COLORS.primary }}
      >
        {display}
      </a>
    );
  }
  if (typeof value === 'number') return value.toFixed(4);
  return display.length > 60 ? `${display.slice(0, 57)}...` : display;
}

export default function DataTable({ data, columns, maxRows = 100 }: DataTableProps) {
  if (!data || data.length === 0) {
    return <p className="text-gray-400 italic text-sm">No data available.</p>;
  }

  const rows = data.slice(0, maxRows);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="max-h-[500px] overflow-auto">
        <table className="w-full text-xs border-collapse">
          <thead className="sticky top-0 z-10">
            <tr className="bg-gray-100 border-b-2 border-gray-300">
              {columns.map(column => (
                <th key={column} className="px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={`border-b border-gray-100 ${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors`}
              >
                {columns.map(column => (
                  <td key={column} className="px-3 py-1.5 text-gray-700 whitespace-nowrap">
                    {cellContent(column, row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.length > maxRows && (
        <div className="px-3 py-1 text-xs text-gray-400 bg-gray-50 border-t">
          Showing {maxRows} of {data.length} rows
        </div>
      )}
    </div>
  );
}
