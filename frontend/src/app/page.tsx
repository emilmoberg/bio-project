"use client";

import React, { useState } from "react";
import axios from "axios";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { Search, Dna, Loader2, ChevronRight, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

type TFResult = {
  matrix_id: string;
  name: string;
  version: string;
  collection: string;
  sequence_logo: string;
  url: string;
};

type TopHit = {
  start: number;
  end: number;
  score: number;
  sequence: string;
};

export default function Home() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [tfList, setTfList] = useState<TFResult[]>([]);
  const [selectedTfId, setSelectedTfId] = useState("");
  const [dnaSequence, setDnaSequence] = useState("");
  const [scores, setScores] = useState<{ position: number; score: number }[]>([]);
  const [topHits, setTopHits] = useState<TopHit[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [sequenceName, setSequenceName] = useState<string>("");

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      setIsSearching(true);
      const res = await axios.get("http://localhost:8000/api/search_tfs", {
        params: { query: searchQuery }
      });
      setTfList(res.data.results);
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error searching TFs",
        description: err.response?.data?.error || "Failed to search transcription factors"
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleScan = async () => {
    try {
      setIsScanning(true);
      const res = await axios.post("http://localhost:8000/api/scan", {
        sequence: dnaSequence,
        tf_id: selectedTfId
      });
      const { scores: rawScores, positions, topHits } = res.data;
      setScores(rawScores.map((s: number, i: number) => ({
        position: positions[i],
        score: s
      })));
      setTopHits(topHits);
      console.log(res.data)
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error scanning sequence",
        description: err.response?.data?.error || "Failed to scan nucleotide sequence"
      });
    } finally {
      setIsScanning(false);
    }
  };

  const handleSequenceChange = (value: string) => {
    setDnaSequence(value);
    // Extract sequence name from FASTA header if present
    if (value.startsWith('>')) {
      const firstLine = value.split('\n')[0];
      setSequenceName(firstLine.substring(1).trim());
    } else {
      setSequenceName("");
    }
  };

  const chartConfig = {

  } satisfies ChartConfig

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Dna className="h-6 w-6" />
        TF Binding Site Scanner
      </h1>
      
      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <Label htmlFor="search">Search and Select Transcription Factors</Label>
              <div className="flex gap-2">
                <Input
                  id="search"
                  placeholder="Search TFs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <Button type="submit" disabled={isSearching}>
                  {isSearching ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </form>

          {tfList.length > 0 && (
            <div className="mt-4">
              <div className="border rounded-lg divide-y overflow-auto max-h-[300px]">
                {tfList.map((tf) => (
                  <div
                    key={tf.matrix_id}
                    className={`p-3 cursor-pointer hover:bg-gray-100 ${
                      selectedTfId === tf.matrix_id ? "bg-gray-100" : ""
                    }`}
                    onClick={() => setSelectedTfId(tf.matrix_id)}
                  >
                    <div className="font-medium flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ChevronRight className="h-4 w-4" />
                        {tf.name}
                      </div>
                      {selectedTfId === tf.matrix_id && (
                        <Check className="size-4" />
                      )}
                    </div>
                    <div className="text-sm text-gray-600 ml-6 space-y-1">
                      <div>{tf.matrix_id} (v{tf.version})</div>
                      <div className="text-xs text-gray-500">{tf.collection}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="sequence">Nucleotide Sequence {sequenceName && <span className="text-sm text-gray-500">({sequenceName})</span>}</Label>
            <Textarea
              id="sequence"
              placeholder="Enter nucleotide sequence or FASTA format..."
              value={dnaSequence}
              onChange={(e) => handleSequenceChange(e.target.value)}
              className="h-32 font-mono"
            />
            <p className="text-sm text-gray-500 mt-1">
              Accepts plain sequence or FASTA format (starting with &gt;)
            </p>
          </div>
          <Button 
            onClick={handleScan}
            disabled={!selectedTfId || !dnaSequence || isScanning}
            className="w-full"
          >
            {isScanning ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Dna className="h-4 w-4 mr-2" />
            )}
            {isScanning ? "Scanning..." : "Scan Sequence"}
          </Button>
          <p className="text-sm text-gray-500 text-center w-full">Selected TF: {tfList.find(tf => tf.matrix_id === selectedTfId)?.name || "None"}</p>

        </div>
      </div>

      {scores.length > 0 && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Binding Score Profile</CardTitle>
            <CardDescription>
              Position-specific binding scores along the sequence
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="max-h-96 w-full">
              <LineChart
                data={scores}
                margin={{ left: 12, right: 12 }}
              >
                <CartesianGrid vertical={false} />
                <XAxis
                  dataKey="position"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                />
                <YAxis
                  tickFormatter={(value) => value.toFixed(2)}
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                />
                <Line
                  dataKey="score"
                  type="monotone"
                  strokeWidth={2}
                  dot={true}
                />
                <ChartTooltip
                  cursor={true}
                  content={<ChartTooltipContent/>}
                />
              </LineChart>
            </ChartContainer>
          </CardContent>
        </Card>
      )}

      {topHits.length > 0 ? (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Top Binding Sites</h2>
          <div className="space-y-2">
            {topHits.map((hit, i) => (
              <div key={i} className="p-3 bg-gray-50 rounded-lg">
                <div>Position {hit.start}-{hit.end}: Score {hit.score.toFixed(2)}</div>
                <div className="text-xs text-gray-500">Sequence: {hit.sequence}</div>
              </div>
            ))}
          </div>
        </div>
      ) : scores.length > 0 && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">No good binding sites found</h2>
        </div>
      )}
    </div>
  );
}