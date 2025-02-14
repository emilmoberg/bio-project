"use client";

import React, { useState } from "react";
import axios from "axios";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { Search, Dna, Loader2, ChevronRight } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

type TFResult = {
  matrix_id: string;
  name: string;
  family: string;
  tax_group: string;
};

type TopHit = {
  start: number;
  end: number;
  score: number;
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
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error scanning sequence",
        description: err.response?.data?.error || "Failed to scan DNA sequence"
      });
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Dna className="h-6 w-6" />
        TF Binding Site Scanner
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <Label htmlFor="tf-search">Search Transcription Factors</Label>
            <form onSubmit={handleSearch} className="flex gap-2 mt-1">
              <Input
                id="tf-search"
                placeholder="e.g. RUNX"
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
              hmm
            </form>
          </div>

          {isSearching ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-gray-200 rounded-lg" />
                </div>
              ))}
            </div>
          ) : (
            tfList.length > 0 && (
              <div className="border rounded-lg overflow-hidden">
                <div className="max-h-64 overflow-y-auto">
                  {tfList.map((tf) => (
                    <div
                      key={tf.matrix_id}
                      className={`p-3 cursor-pointer hover:bg-gray-100 ${
                        selectedTfId === tf.matrix_id ? "bg-gray-200" : ""
                      }`}
                      onClick={() => setSelectedTfId(tf.matrix_id)}
                    >
                      <div className="font-medium flex items-center gap-2">
                        <ChevronRight className="h-4 w-4" />
                        {tf.name}
                      </div>
                      <div className="text-sm text-gray-600 ml-6">
                        {tf.matrix_id} - {tf.family}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          )}
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="sequence">DNA Sequence</Label>
            <Textarea
              id="sequence"
              placeholder="Enter DNA sequence..."
              value={dnaSequence}
              onChange={(e) => setDnaSequence(e.target.value)}
              className="h-32"
            />
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
        </div>
      </div>

      {scores.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Binding Score Profile</h2>
          <div className="border rounded-lg p-4 bg-white">
            <LineChart width={800} height={300} data={scores}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="position" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#4f46e5" />
            </LineChart>
          </div>
        </div>
      )}

      {topHits.length > 0 && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Top Binding Sites</h2>
          <div className="space-y-2">
            {topHits.map((hit, i) => (
              <div key={i} className="p-3 bg-gray-50 rounded-lg">
                Position {hit.start}-{hit.end}: Score {hit.score.toFixed(2)}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}