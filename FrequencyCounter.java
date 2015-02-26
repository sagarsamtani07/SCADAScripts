package ShodanClassification;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class FrequencyCounter {
	
	private static String[] dictChars1={"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","%","@","-","0","1","2","3","4","5","6","7","8","9"};
	private static String[] dictChars2={"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","%","@","-","0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"};
	private static String[] dictChars;
	
	public int getIgnorecase()
	{
		if(dictChars.equals(dictChars1)) return 1;
		else return 0;
	}
	
	public long getFrequency(String msg, String regExp)
	{
		long counter=0;
		try{
		Pattern pattern=Pattern.compile(regExp);
		Matcher m= pattern.matcher(msg);
		while(m.find())
		{
			counter++;
		}
		return counter;
		}
		catch(Exception e)
		{System.out.println(regExp+"---"+msg);
		return counter;}
		
	}
	
	public long getFrequency(String[] words, String word)
	{
		long counter=0;
		for(int i=0;i<words.length;i++)
		{
			if(words[i].equals(word))
				counter++;
		}
		
		return counter;
	}
	
	public long getWordCount(String msg)
	{
		return getFrequency(msg.trim().replaceAll("[.|,|-|?|!|~|^|:|;|'|\"|=|*|&|#|$]", "").trim()," ++")+1;
	}
	
	public long getCharacterCount(String msg)
	{
		return msg.replaceAll(" ","").trim().length();
	}
	
	public long getHapaxBeta(String msg, int occurenceTime,Set<String> WORDS,String[] words)
	{
		//long N=getWordCount(msg);
		//Set<String> WORDS=makeDictionary(msg,1);
		long count=0;
		for(String word:WORDS)
		{
			if(getFrequency(msg.toLowerCase(), word)==(long)occurenceTime) count++;
		}
		return count;
	}
	
	public long getHapax(String msg, int occurenceTime,Set<String> WORDS,String[] words)
	{
		//long N=getWordCount(msg);
		//Set<String> WORDS=makeDictionary(msg,1);
		long count=0;
		Map<String,Long> countMatrix=new HashMap<String,Long>();
		for(String word:WORDS)
		{
			countMatrix.put(word, (long) 0);
		}
		for(int i=0;i<words.length;i++)
		{
			if(countMatrix.containsKey(words[i].toLowerCase()))
			{
				long num=countMatrix.get(words[i].toLowerCase());
				countMatrix.put(words[i].toLowerCase(),(long)(num+1));
			}
				
		}
		for(String word:WORDS)
		{
			if(countMatrix.get(word)==(long)occurenceTime)
				count++;
		}
		return count;
	}
	
	public long getHapax(String msg, int occurenceTime)
	{
		//long N=getWordCount(msg);
		Set<String> WORDS=makeDictionary(msg,1);
		String[] words=msg.trim().replaceAll("\\+"," plus ").replaceAll("[.|,|-|?|!|~|^|:|;|'|\"|=|*|&|#|$|\\(|\\)|\\[|\\]|<|>]","").trim().split(" ++");
		return getHapax(msg,occurenceTime,WORDS,words);
	}
	
	public Set<String> makeDictionary(String msg,int ngram)
	{
		String[] words=msg.trim().replaceAll("\\+"," plus ").replaceAll("[.|,|-|?|!|~|^|:|;|'|\"|=|*|&|#|$|\\(|\\)|\\[|\\]|<|>|\\+]","").trim().split(" ++");
		Set<String> WORDS=new TreeSet<String>();

		for(int i=0;i<words.length;i++)
		{
			WORDS.add(words[i].toLowerCase());
		}
		if(ngram==1) 
			return WORDS;
		else
		{
			System.out.println("Start creating ngram dictionary.....\n");
			String[] sentences= msg.trim().split("\\.+(\\s|$)?|\\?(\\s|$)?|\\!(\\s|$)?|\\!(\\s|$)?|;(\\s|$)?|\\,(\\s|$)?|\"(\\s|$)?|:(\\s|$)?|'(\\s|$)?");
			int size=sentences.length;
			for(int gramsize=2;gramsize<=ngram;gramsize++)
			{
				for(int sentenceNo=0;sentenceNo<size;sentenceNo++)
				{
					System.out.println("Creating "+gramsize+" size grams for sentence "+sentenceNo+"/"+size+"=.....");
					String[] wordsInSentence=sentences[sentenceNo].trim().replaceAll("[.|,|-|?|!|~|^|:|;|'|\"|=|*|&|#|$|\\(|\\)|\\[|\\]|<|>|\\+]","").trim().split(" ++");
					int subsize=wordsInSentence.length;
					if(gramsize<=subsize)
					{
						for(int i=0;i<=subsize-gramsize;i++)
						{
							StringBuilder wordngram=new StringBuilder();
							for(int j=1;j<=gramsize;j++)
							{
								wordngram.append(wordsInSentence[i+j-1].toLowerCase()+" ");
							}
							WORDS.add(wordngram.toString().trim());
						}
					}
				}
			}
			
			return WORDS;
		}
	}
	
	
	
	public Set<String> makeCharDictionary(int ngram, int ignoreCase)
	{
		
		if(ignoreCase==1)
			dictChars=dictChars1;
		else
			dictChars=dictChars2;
		Set<String> WORDS=new TreeSet<String>();
		if(ngram==1)
		{
			for(int i=0;i<dictChars.length;i++)
				WORDS.add(dictChars[i]);
			return WORDS;
		}
		else
		{
			StringBuilder charngram=new StringBuilder();
			Set<String> COMBINATIONS=makeCharDictionary(ngram-1,ignoreCase);
			for(int i=0;i<dictChars.length;i++)
			{
				charngram=new StringBuilder();
				String temp=charngram.append(dictChars[i]).toString();
				for(String combination:COMBINATIONS)
				{
					charngram=new StringBuilder();
					charngram.append(temp).append(combination);
					WORDS.add(charngram.toString());
				}
			}
			WORDS.addAll(COMBINATIONS);
			return WORDS;
		}

	}
	
	
	public Map<String,Long> getCountMatrix(String msg,int ngram)
	{
		Set<String> ENTIRE=makeDictionary(msg, ngram);
		return getCountMatrix(msg,ENTIRE,ngram);
	}
	
	public Map<String,Long> getCountMatrix(String msg,Set<String> ENTIRE,int ngram)
	{
		
		Map<String,Long> countMatrix=new TreeMap<String,Long>();
		for(String word:ENTIRE)
		{
			countMatrix.put(word, (long) 0);
		}
		
		String[] sentences= msg.toString().trim().split("\\.+(\\s|$)?|\\?(\\s|$)?|\\!(\\s|$)?|\\!(\\s|$)?|;(\\s|$)?|\\,(\\s|$)?|\"(\\s|$)?|:(\\s|$)?|'(\\s|$)?");
		int size=sentences.length;
		for(int gramsize=1;gramsize<=ngram;gramsize++)
		{
			for(int sentenceNo=0;sentenceNo<size;sentenceNo++)
			{
				try{
					if(sentenceNo%10000==0)
						System.out.println("Counting "+gramsize+" size grams in sentence "+sentenceNo+"/"+size+".....");
					String[] wordsInSentence=sentences[sentenceNo].trim().replaceAll("[\n|\r|.|,|-|?|!|~|^|:|;|'|\"|=|*|&|#|$|\\(|\\)|\\[|\\]|<|>|\\+]","").trim().split(" ++");
					int subsize=wordsInSentence.length;
					if(gramsize<=subsize)
					{
						for(int i=0;i<=subsize-gramsize;i++)
						{
							StringBuilder wordngram=new StringBuilder();
							for(int j=1;j<=gramsize;j++)
							{
								wordngram.append(wordsInSentence[i+j-1].toLowerCase()+" ");
							}
							String nextNngram=wordngram.toString().trim();
							if(countMatrix.containsKey(nextNngram))
							{
								long num=countMatrix.get(nextNngram);
								countMatrix.put(nextNngram,(long)(num+1));
							}
					
						}
					}
				}
				catch(Exception e){
					String s=sentences[sentenceNo];
					System.out.println(s);
					}
			}
		}
		
		return countMatrix;
	}
}
