.PHONY: run
run:
	go run main.go    # compile + run immediately

.PHONY: build
build:
	go build main.go  # creates ./main binary
	./main            # run the binary

.PHONY: clean
clean:
	go clean 		  # clean build files

