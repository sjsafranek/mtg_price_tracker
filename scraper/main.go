package main

import (
	"encoding/csv"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"strings"
	"sync"
	"flag"

	"github.com/PuerkitoBio/goquery"
)

const (
	DEFAULT_MTG_FORMAT string = "Pioneer"
	BASE_URL string = "https://mtgdecks.net"
)

var (
	MTG_FORMAT string = DEFAULT_MTG_FORMAT
)

func checkError(message string, err error) {
	if nil != err {
		log.Fatal(message, err)
	}
}

func FetchPage(url string) *goquery.Document {
	log.Println(url)
	doc, err := goquery.NewDocument(url)
	checkError("Unable to fetch page", err)
	return doc
}

func FetchArchetypeURLs(mtgFormat string) ([]string, error) {
	page := FetchPage(fmt.Sprintf("%v/%v", BASE_URL, mtgFormat))
	urls := []string{}
	page.Find("#archetypes a").Each(func(index int, item *goquery.Selection) {
		href, _ := item.Attr("href")
		urls = append(urls, href)
	})
	return urls, nil
}

type CardEntry struct {
	Amount int    `json:"amount"`
	Name   string `json:"name"`
}

type Deck struct {
	Format string `json:"format"`
	Archetype string       `json:"archetype"`
	Name      string       `json:"name"`
	Creator   string       `json:"creator"`
	URL       string       `json:"url"`
	MainBoard []*CardEntry `json:"mainboard"`
	SideBoard []*CardEntry `json:"sideboard"`
}

func ParseDeck(deckText string) *Deck {
	var deck Deck

	lines := strings.Split(deckText, "\n")
	for i, line := range lines {

		if 0 == i {
			line = strings.Replace(line, "//", "", -1)
			line = strings.Replace(line, " (dec) Version", "", -1)
			parts := strings.Split(line, " a Pioneer deck by ")
			log.Println(line, parts)
			if 2 == len(parts) {
				deck.Name = parts[0]
				deck.Creator = parts[1]
			}
			continue
		}

		if "" == line || "// Sideboard:" == line {
			continue
		}

		if strings.Contains(line, "SB: ") {
			// Side board cards
			line = strings.Replace(line, "SB: ", "", -1)

			fIdx := strings.Index(line, " ")
			amount, err := strconv.Atoi(line[:fIdx])
			checkError("Unable to parse deck", err)

			card := CardEntry{Amount: amount, Name: line[fIdx+1:]}
			deck.MainBoard = append(deck.MainBoard, &card)
			continue
		} else {
			// Main board cards
			fIdx := strings.Index(line, " ")
			amount, err := strconv.Atoi(line[:fIdx])
			checkError("Unable to parse deck", err)

			card := CardEntry{Amount: amount, Name: line[fIdx+1:]}
			deck.SideBoard = append(deck.SideBoard, &card)
		}

	}

	return &deck
}

func FetchDeck(mtgFormat, archetype, deckUrl string) *Deck {
	url := fmt.Sprintf("%v/%v/dec", BASE_URL, deckUrl)
	resp, err := httpClient.Get(url)
	checkError("Unable to fetch deck", err)

	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	checkError("Unable to read response body", err)

	deck := ParseDeck(string(body))
	deck.URL = deckUrl
	deck.Format = mtgFormat
	deck.Archetype = archetype
	return deck
}

func FetchDecks(mtgFormat string, archetype string, pageNumber int) []string {
	page := FetchPage(fmt.Sprintf("%v/%v/%v/page:%v", BASE_URL, mtgFormat, archetype, fmt.Sprintf("%v", pageNumber)))

	// check current page
	elem := page.Find(".pagination .active")
	if elem.Text() != fmt.Sprintf("%v", pageNumber) {
		return []string{}
	}

	urls := []string{}
	// page.Find("tr.previewable td a").Each(func(index int, item *goquery.Selection) {
	page.Find(".clickable.table.table-striped tbody td a").Each(func(index int, item *goquery.Selection) {
		href, _ := item.Attr("href")
		urls = append(urls, href)
	})

	return append(urls, FetchDecks(mtgFormat, archetype, 1+pageNumber)...)
}

func Worker(mtgFormat string, archetype string, wg *sync.WaitGroup, outch chan *Deck) {
	urls := FetchDecks(mtgFormat, archetype, 1)
	for _, url := range urls {
		deck := FetchDeck(mtgFormat, archetype, url)
		outch <- deck
	}
	wg.Done()
}

func init() {
	flag.StringVar(&MTG_FORMAT, "format", DEFAULT_MTG_FORMAT, "Magic the Gathering format")
	flag.Parse()
}

func main() {

	urls, _ := FetchArchetypeURLs(MTG_FORMAT)

	var writerWg sync.WaitGroup
	writerWg.Add(1)
	var decksWg sync.WaitGroup
	deckChannel := make(chan *Deck, 10)

	outFile, err := os.Create("decks.csv")
	checkError("Unable to open file", err)

	writer := csv.NewWriter(outFile)
	defer writer.Flush()

	writer.Write([]string{"format","archetype","deck_name","creator","amount","card_name","section","url"})
	go func() {
		for deck := range deckChannel {
			for _, card := range deck.MainBoard {
				_ = writer.Write([]string{deck.Format, deck.Archetype, deck.Name, deck.Creator, fmt.Sprintf("%v", card.Amount), card.Name, "MainBoard", deck.URL})
			}
			for _, card := range deck.SideBoard {
				_ = writer.Write([]string{deck.Format, deck.Archetype, deck.Name, deck.Creator, fmt.Sprintf("%v", card.Amount), card.Name, "SideBoard", deck.URL})
			}
		}
		writerWg.Done()
	}()

	for _, url := range urls {
		decksWg.Add(1)
		archetype := strings.Split(url, "/")[2]
		go Worker(MTG_FORMAT, archetype, &decksWg, deckChannel)
	}

	decksWg.Wait()
	close(deckChannel)
	writerWg.Wait()
}
